from __future__ import annotations
from typing import Iterable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from .config import settings

def format_context(docs) -> str:
    blocks = []
    for d in docs:
        pmid = d.metadata.get("pmid", "?")
        blocks.append(f"[PMID:{pmid}]\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)

def format_sources(docs) -> list[str]:
    seen, out = set(), []
    for d in docs:
        pmid = d.metadata.get("pmid", None)
        if pmid and pmid not in seen:
            seen.add(pmid)
            out.append(f"PMID:{pmid}")
    return out

def load_index(api_key: str):
    s = settings()
    embeddings = OpenAIEmbeddings(model=s.embedding_model, api_key=api_key)
    vs = FAISS.load_local(str(s.index_dir), embeddings, allow_dangerous_deserialization=True)
    retriever = vs.as_retriever(search_type=s.search_type, search_kwargs={"k": s.k, "fetch_k": s.fetch_k})
    return vs, retriever

def build_chat(api_key: str):
    s = settings()
    _, retriever = load_index(api_key)
    llm = ChatOpenAI(model=s.chat_model, temperature=s.temperature, api_key=api_key)

    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", "Rewrite the user's latest question into a standalone literature question using chat history. Return ONLY the question."),
        MessagesPlaceholder("history"),
        ("human", "{input}")
    ])
    rewrite_chain = rewrite_prompt | llm | StrOutputParser()

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a medical literature assistant based ONLY on the provided abstracts.\n"
         "Rules:\n"
         "- Do not invent studies, numbers, or conclusions not present in the context.\n"
         "- If evidence is incomplete, say so.\n"
         "- Include PMID citations after key claims like (PMID:123...).\n"
         "- Not medical advice."),
        MessagesPlaceholder("history"),
        ("human", "Question: {question}\n\nAbstract context:\n{context}\n\nAnswer (with PMID citations):")
    ])

    rag_chain = (
        RunnablePassthrough.assign(question=rewrite_chain)
        .assign(docs=(lambda x: x["question"]) | retriever)
        .assign(context=(lambda x: x["docs"]) | RunnableLambda(format_context))
        .assign(output=answer_prompt | llm | StrOutputParser())
    )

    store: dict[str, InMemoryChatMessageHistory] = {}

    def get_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    chat = RunnableWithMessageHistory(
        rag_chain,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    def ask(q: str, session_id: str = "default"):
        out = chat.invoke({"input": q}, config={"configurable": {"session_id": session_id}})
        return out["output"], format_sources(out["docs"])

    return ask
