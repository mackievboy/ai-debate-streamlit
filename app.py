from __future__ import annotations

import base64
from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

from debate import DEFAULT_MODELS, PROVIDER_NAMES, ProviderId, run_debate


st.set_page_config(
    page_title="AI Debate",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSET_DIR = Path(__file__).resolve().parent / "assets"
PROVIDER_META = {
    "chatgpt": {"label": "OpenAI · ChatGPT", "color": "#16866f", "icon": "openai.svg"},
    "claude": {"label": "Anthropic · Claude", "color": "#b45b35", "icon": "claude.svg"},
    "gemini": {"label": "Google · Gemini", "color": "#5b7fdc", "icon": "gemini.svg"},
}


def asset_data_uri(filename: str) -> str:
    payload = base64.b64encode((ASSET_DIR / filename).read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{payload}"


def inject_styles() -> None:
    mountain_uri = asset_data_uri("sidebar-mountain.svg")
    css = """
    <style>
    :root { --ink:#17233b; --muted:#7d899d; --line:#d8e0eb; --blue:#286ed5; --bg:#f3f5f9; }
    html,body,[class*="css"] { font-family:Inter,-apple-system,BlinkMacSystemFont,"Noto Sans KR",sans-serif; }
    .stApp { color:var(--ink); background:var(--bg); }
    [data-testid="stHeader"],[data-testid="stToolbar"] { display:none !important; }
    [data-testid="stAppViewContainer"] > div:not([data-testid="stSidebar"]) { position:relative !important; flex:1 1 auto; min-width:0; }
    [data-testid="stMain"] { background:linear-gradient(180deg,#f7f8fb,#f2f4f8); }
    .block-container { max-width:1540px; padding:2rem 2.7rem 4.5rem; }

    section[data-testid="stSidebar"] {
      width:268px !important; min-width:268px !important; border:0;
      background:#132746 url("__MOUNTAIN_URI__") center/cover no-repeat;
      box-shadow:8px 0 28px #13233b17; overflow:hidden;
    }
    section[data-testid="stSidebar"] > div { background:transparent; }
    [data-testid="stSidebarContent"] { position:relative; z-index:2; padding:1.5rem 1rem; }
    [data-testid="stSidebarCollapseButton"] { display:none; }
    .side-brand { display:flex; align-items:center; gap:.8rem; padding:.15rem .45rem 1.8rem; color:#f8fbff; }
    .side-logo { display:grid; place-items:center; width:43px; height:43px; border-radius:13px; background:linear-gradient(145deg,#2488f3,#1b5fd2); box-shadow:0 9px 22px #07182f70; font-size:.75rem; font-weight:900; letter-spacing:.12em; }
    .side-brand strong { display:block; font-size:1.08rem; letter-spacing:-.025em; }
    .side-brand span { display:block; color:#a6b6cf; font-size:.6rem; font-weight:800; letter-spacing:.12em; margin-top:.16rem; }
    [data-testid="stSidebar"] [role="radiogroup"] { gap:.42rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label { min-height:3.15rem; padding:.75rem .9rem; border-radius:11px; color:#abb9ce; transition:.15s ease; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { color:#fff; background:#ffffff0d; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { color:#fff; background:#395a87; box-shadow:0 9px 23px #07162b4a; }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child { display:none !important; }
    [data-testid="stSidebar"] [role="radiogroup"] p { color:inherit !important; font-size:.92rem; font-weight:720; }
    .side-foot { position:fixed; left:1.75rem; bottom:1.6rem; z-index:4; color:#d8e2ef; }
    .side-foot strong { display:block; font-size:.78rem; line-height:1.5; letter-spacing:.025em; }
    .side-foot span { display:block; margin-top:.55rem; color:#9dadc6; font-size:.61rem; }

    h1,h2,h3 { color:var(--ink) !important; letter-spacing:-.035em !important; }
    p,.stCaption { color:var(--muted); }
    .page-head { display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; margin-bottom:1.3rem; }
    .page-head .eyebrow { color:#286ed5; font-size:.62rem; font-weight:850; letter-spacing:.16em; }
    .page-head h1 { margin:.25rem 0 .18rem; font-size:2rem; line-height:1.15; }
    .page-head p { margin:0; color:#7c889b; font-size:.8rem; }
    .status-pill { flex:none; color:#3e5f89; background:#eaf1fc; border:1px solid #cad8ed; border-radius:999px; padding:.48rem .72rem; font-size:.68rem; font-weight:780; }

    [data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border-color:var(--line); border-radius:13px; box-shadow:0 7px 22px #3d557609; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-marker) { padding:1.05rem 1.15rem .8rem; }
    .card-title { display:flex; align-items:center; justify-content:space-between; color:#2c3a52; font-size:.78rem; font-weight:820; margin-bottom:.45rem; }
    .card-title span { color:#96a1b2; font-size:.62rem; font-weight:650; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-marker) textarea { min-height:178px; padding:1rem; background:#fbfcfe; border:1px solid #d6deea; border-radius:10px; color:#1c2940; font-size:1rem; line-height:1.62; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-marker) textarea:focus { border-color:#5f94dc; box-shadow:0 0 0 3px #286ed518; }
    .composer-foot { display:flex; align-items:center; justify-content:space-between; color:#96a1b2; font-size:.62rem; margin-top:-.25rem; }
    .section-head { display:flex; align-items:end; justify-content:space-between; margin:1.55rem 0 .72rem; }
    .section-head h2 { margin:0; font-size:1.12rem; }
    .section-head p { margin:.18rem 0 0; font-size:.68rem; }
    .section-head span { color:#61718a; font-size:.66rem; font-weight:760; }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.provider-marker) { position:relative; overflow:hidden; min-height:194px; padding:.95rem .95rem .72rem; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.provider-marker)::before { content:""; position:absolute; inset:0 auto 0 0; width:4px; background:#c9d2df; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.provider-marker.selected)::before { background:var(--provider); }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.provider-marker.selected) { border-color:color-mix(in srgb,var(--provider) 40%,#d8e0eb); }
    .provider-head { display:flex; align-items:center; gap:.68rem; margin:.05rem 0 .65rem; }
    .provider-head img { width:40px; height:40px; flex:none; }
    .provider-head strong { display:block; color:var(--provider); font-size:.95rem; }
    .provider-head span { display:block; color:#8a96a7; font-size:.6rem; margin-top:.12rem; }
    .provider-mode { display:flex; align-items:center; justify-content:space-between; gap:.5rem; border:1px solid #e0e5ed; background:#f8f9fc; border-radius:8px; padding:.55rem .65rem; margin:.18rem 0 .45rem; }
    .provider-mode span { color:#8a95a7; font-size:.59rem; font-weight:760; }
    .provider-mode strong { color:#4c5a70; font-size:.64rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .api-line { display:flex; align-items:center; gap:.35rem; color:#718096; font-size:.61rem; }
    .api-line i { width:7px; height:7px; border-radius:50%; background:#c6ced9; }
    .api-line.ready i { background:#14934c; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.provider-marker) [data-testid="stCheckbox"] label { color:#526078; margin-top:.08rem; }

    [data-testid="stVerticalBlockBorderWrapper"]:has(.finalizer-marker) { margin-top:.8rem; padding:.8rem 1rem .65rem; }
    .helper-text { color:#7e8a9d; font-size:.64rem; margin-top:.15rem; }
    [data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input,[data-testid="stSelectbox"] > div > div { color:#1d293d; background:#fff; border-color:#d4dce8; border-radius:9px; }

    .right-hero { display:block; width:100%; height:154px; object-fit:cover; border:1px solid #d4dce8; border-radius:13px; box-shadow:0 7px 20px #3e57750d; }
    .right-card { margin-top:.8rem; background:#fff; border:1px solid var(--line); border-radius:13px; padding:1rem 1.05rem; box-shadow:0 7px 22px #3d557609; }
    .right-card h3 { margin:0 0 .8rem; font-size:.94rem; }
    .connection-row { display:grid; grid-template-columns:34px 1fr auto; align-items:center; gap:.58rem; padding:.58rem 0; border-bottom:1px solid #edf0f4; }
    .connection-row:last-child { border-bottom:0; }
    .connection-row img { width:34px; height:34px; }
    .connection-row strong { color:#26344c; font-size:.72rem; }
    .api-badge { display:flex; align-items:center; gap:.3rem; color:#718096; background:#f4f6f9; border:1px solid #dde3eb; border-radius:7px; padding:.34rem .45rem; font-size:.58rem; font-weight:760; }
    .api-badge i { width:6px; height:6px; border-radius:50%; background:#c3cad5; }
    .api-badge.ready i { background:#16934c; }
    .summary-list { display:grid; gap:.55rem; }
    .summary-row { display:flex; align-items:center; justify-content:space-between; color:#7d899b; font-size:.66rem; }
    .summary-row strong { color:#26354d; font-size:.68rem; }
    .summary-note { margin-top:.75rem; padding-top:.72rem; border-top:1px solid #e9edf2; color:#8a95a6; font-size:.61rem; line-height:1.5; }

    .stButton > button[kind="primary"] { min-height:3rem; color:#fff; background:#286ed5; border:0; border-radius:9px; box-shadow:0 9px 21px #286ed52b; font-weight:820; }
    .stButton > button[kind="primary"]:hover { background:#1e61c2; }
    .stButton > button[kind="primary"]:disabled { color:#fff; background:#c2cee1; box-shadow:none; opacity:1; }
    .stButton > button:not([kind="primary"]) { color:#344159; background:#fff; border-color:#d6deea; border-radius:9px; }
    .start-wrap { margin-top:.8rem; }

    .progress-card,.result-card,.empty-card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1.25rem; box-shadow:0 9px 26px #3c55760c; }
    .progress-title { display:flex; align-items:center; gap:.65rem; margin-bottom:1rem; }
    .progress-title b { display:grid; place-items:center; width:34px; height:34px; border-radius:50%; color:#286ed5; background:#eaf1fc; }
    .progress-title strong { display:block; font-size:.86rem; }
    .progress-title span { display:block; color:#8793a5; font-size:.62rem; margin-top:.12rem; }
    .timeline-step { display:grid; grid-template-columns:27px 1fr auto; gap:.7rem; align-items:center; padding:.72rem 0; border-top:1px solid #edf0f4; opacity:.48; }
    .timeline-step.active,.timeline-step.done { opacity:1; }
    .timeline-step > b { display:grid; place-items:center; width:27px; height:27px; border-radius:50%; color:#728096; background:#eef1f5; font-size:.62rem; }
    .timeline-step.active > b { color:#fff; background:#286ed5; }
    .timeline-step.done > b { color:#16866f; background:#e6f4ef; }
    .timeline-step strong { display:block; color:#2b3850; font-size:.72rem; }
    .timeline-step span { color:#8995a6; font-size:.6rem; }
    .timeline-state { color:#286ed5 !important; font-weight:760; }
    .result-card { border-top:4px solid #286ed5; }
    .result-card .label { color:#286ed5; font-size:.62rem; font-weight:850; letter-spacing:.14em; }
    .security { margin-top:1rem; padding:.85rem .95rem; color:#367b6e; background:#edf8f5; border:1px solid #bedfd5; border-radius:10px; font-size:.7rem; }
    [data-testid="stStatusWidget"] { background:#fff; border-color:#d8e0eb; border-radius:13px; }

    @media(max-width:1050px){
      section[data-testid="stSidebar"] { width:224px !important; min-width:224px !important; }
      .block-container { padding:1.7rem 1.4rem 4rem; }
      [data-testid="stHorizontalBlock"] { flex-wrap:wrap; gap:1rem; }
      [data-testid="column"] { width:100% !important; min-width:100% !important; flex:1 1 100% !important; }
    }
    @media(max-width:760px){
      .block-container { padding:1.2rem .9rem 3rem; }
      .page-head { align-items:flex-start; flex-direction:column; }
      .side-foot { display:none; }
    }
    </style>
    """.replace("__MOUNTAIN_URI__", mountain_uri)
    st.markdown(css, unsafe_allow_html=True)


def init_state() -> None:
    defaults = {
        "api_keys": {provider: "" for provider in PROVIDER_NAMES},
        "models": DEFAULT_MODELS.copy(),
        "history": [],
        "result": None,
        "last_stage": "idle",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def page_heading(kicker: str, title: str, copy: str, badge: str | None = None) -> None:
    badge_html = f'<span class="status-pill">{escape(badge)}</span>' if badge else ""
    st.markdown(
        f'<div class="page-head"><div><span class="eyebrow">{escape(kicker)}</span>'
        f'<h1>{escape(title)}</h1><p>{escape(copy)}</p></div>{badge_html}</div>',
        unsafe_allow_html=True,
    )


def provider_panel(provider: ProviderId, selected: bool) -> None:
    meta = PROVIDER_META[provider]
    icon = asset_data_uri(meta["icon"])
    ready = bool(st.session_state.api_keys[provider])
    selected_class = " selected" if selected else ""
    ready_class = " ready" if ready else ""
    model = escape(st.session_state.models[provider])
    st.markdown(
        f'<span class="provider-marker{selected_class}" style="--provider:{meta["color"]}"></span>'
        f'<div class="provider-head" style="--provider:{meta["color"]}"><img src="{icon}" alt="">'
        f'<div><strong>{PROVIDER_NAMES[provider]}</strong><span>{meta["label"]}</span></div></div>'
        f'<div class="provider-mode"><span>API MODEL</span><strong>{model}</strong></div>'
        f'<div class="api-line{ready_class}"><i></i>{"API 연결됨" if ready else "API 키 필요"}</div>',
        unsafe_allow_html=True,
    )


def connection_card_html() -> str:
    rows = []
    for provider in PROVIDER_NAMES:
        meta = PROVIDER_META[provider]
        icon = asset_data_uri(meta["icon"])
        ready = bool(st.session_state.api_keys[provider])
        ready_class = " ready" if ready else ""
        rows.append(
            f'<div class="connection-row"><img src="{icon}" alt=""><strong>{PROVIDER_NAMES[provider]}</strong>'
            f'<span class="api-badge{ready_class}">API <i></i></span></div>'
        )
    return '<div class="right-card"><h3>AI 연결 상태</h3>' + "".join(rows) + "</div>"


def render_result(result: dict | None) -> None:
    if not result:
        page_heading("COUNCIL RESULT", "최종 결과", "완료된 토론의 종합 답변을 확인합니다.")
        st.markdown('<div class="empty-card">아직 완료된 토론이 없습니다.</div>', unsafe_allow_html=True)
        return
    page_heading("COUNCIL RESULT", "최종 결과", result["question"])
    st.markdown(
        f'<div class="result-card"><div class="label">FINAL SYNTHESIS</div>'
        f'<h3>{PROVIDER_NAMES[result["finalizer"]]}의 종합 답변</h3></div>',
        unsafe_allow_html=True,
    )
    st.markdown(result["final_answer"])
    with st.expander(f'초기 독립 답변 · {len(result["answers"])}'):
        for answer in result["answers"]:
            st.markdown(f'**{PROVIDER_NAMES[answer["provider"]]}**')
            st.markdown(answer["text"])
            st.divider()
    with st.expander(f'익명 상호 비평 · {len(result["critiques"])}'):
        for critique in result["critiques"]:
            st.markdown(f'**{PROVIDER_NAMES[critique["provider"]]}**')
            st.markdown(critique["text"])
            st.divider()
    st.download_button(
        "최종 답변 TXT 다운로드",
        result["final_answer"],
        file_name=f'ai-debate-{result["id"][:8]}.txt',
        mime="text/plain",
    )


inject_styles()
init_state()

with st.sidebar:
    st.markdown(
        '<div class="side-brand"><div class="side-logo">•••</div><div><strong>AI Debate</strong>'
        '<span>WEB · STREAMLIT</span></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "메뉴",
        ["✎　새 토론", "⌛　진행", "▤　결과", "◷　기록", "⚙　설정"],
        label_visibility="collapsed",
    )
    st.markdown(
        '<div class="side-foot"><strong>Think together.<br>Decide better.</strong>'
        '<span>🔒 API 키는 저장하지 않습니다.</span></div>',
        unsafe_allow_html=True,
    )


if "새 토론" in page:
    key_count = sum(bool(value) for value in st.session_state.api_keys.values())
    page_heading(
        "NEW DEBATE",
        "새 토론",
        "질문을 입력하고 함께 토론할 AI를 선택하세요.",
        f"API 연결 {key_count} / 3",
    )

    main_column, right_column = st.columns([2.45, 0.82], gap="large")
    with main_column:
        with st.container(border=True):
            st.markdown(
                '<span class="composer-marker"></span><div class="card-title">토론 질문'
                '<span>무엇이든 물어보세요</span></div>',
                unsafe_allow_html=True,
            )
            question = st.text_area(
                "토론 질문",
                placeholder="예: 원격근무가 조직의 장기 생산성에 미치는 영향을 분석해줘.",
                height=178,
                max_chars=12_000,
                key="debate_question",
                label_visibility="collapsed",
            )
            st.markdown(
                f'<div class="composer-foot"><span>독립 답변 → 익명 비평 → 최종 종합</span>'
                f'<span>{len(question):,} / 12,000</span></div>',
                unsafe_allow_html=True,
            )

        selected_before = {
            provider: bool(st.session_state.get(f"participant_{provider}", True))
            for provider in PROVIDER_NAMES
        }
        st.markdown(
            f'<div class="section-head"><div><h2>토론 참여 AI</h2><p>최소 두 개의 AI를 선택하세요.</p></div>'
            f'<span>{sum(selected_before.values())}개 참여</span></div>',
            unsafe_allow_html=True,
        )
        provider_columns = st.columns(3, gap="medium")
        selected: list[ProviderId] = []
        for column, provider in zip(provider_columns, PROVIDER_NAMES):
            with column:
                with st.container(border=True):
                    provider_panel(provider, selected_before[provider])
                    enabled = st.checkbox(
                        "토론 참여",
                        value=True,
                        key=f"participant_{provider}",
                    )
                if enabled:
                    selected.append(provider)

        with st.container(border=True):
            st.markdown('<span class="finalizer-marker"></span>', unsafe_allow_html=True)
            finalizer: ProviderId | None = None
            if selected:
                finalizer = st.selectbox(
                    "최종 종합 AI",
                    selected,
                    format_func=lambda provider: PROVIDER_NAMES[provider],
                )
            st.markdown(
                '<div class="helper-text">선택한 AI가 독립 답변과 비평을 하나의 최종안으로 종합합니다.</div>',
                unsafe_allow_html=True,
            )

    missing_keys = [provider for provider in selected if not st.session_state.api_keys[provider]]
    call_count = len(selected) * 2 + 1 if selected else 0
    with right_column:
        st.markdown(
            f'<img class="right-hero" src="{asset_data_uri("council-banner.svg")}" alt="산과 호수 일러스트">',
            unsafe_allow_html=True,
        )
        st.markdown(connection_card_html(), unsafe_allow_html=True)
        finalizer_name = PROVIDER_NAMES[finalizer] if finalizer else "-"
        missing_note = (
            "설정에서 선택한 AI의 API 키를 먼저 입력하세요."
            if missing_keys
            else "선택한 AI의 API를 사용합니다."
        )
        st.markdown(
            '<div class="right-card"><h3>예상 토론</h3><div class="summary-list">'
            '<div class="summary-row"><span>전략</span><strong>익명 상호 비평</strong></div>'
            f'<div class="summary-row"><span>참여 AI</span><strong>{len(selected)}개</strong></div>'
            f'<div class="summary-row"><span>최종 종합</span><strong>{finalizer_name}</strong></div>'
            f'<div class="summary-row"><span>예상 호출</span><strong>{call_count}회</strong></div>'
            f'</div><div class="summary-note">{missing_note}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="start-wrap"></div>', unsafe_allow_html=True)
        start_clicked = st.button(
            "토론 시작　→",
            type="primary",
            use_container_width=True,
            disabled=(
                len(question.strip()) < 3
                or len(selected) < 2
                or finalizer is None
                or bool(missing_keys)
            ),
        )

    if start_clicked:
        try:
            with st.status("토론을 시작합니다...", expanded=True) as status:
                def update_progress(stage: str, message: str) -> None:
                    st.session_state.last_stage = stage
                    status.write(message)

                result = run_debate(
                    question,
                    selected,
                    finalizer,
                    st.session_state.api_keys,
                    st.session_state.models,
                    update_progress,
                )
                st.session_state.result = result
                st.session_state.history.insert(0, result)
                st.session_state.history = st.session_state.history[:30]
                status.update(label="최종 합의안을 완성했습니다.", state="complete")
            render_result(result)
        except Exception as error:
            st.session_state.last_stage = "error"
            st.error(str(error))

elif "진행" in page:
    page_heading("LIVE DEBATE", "토론 진행", "선택한 AI가 단계별로 답변과 비평을 만들고 있습니다.")
    stage = st.session_state.last_stage
    stage_labels = {
        "idle": "토론 시작 대기 중",
        "initial": "독립 답변 생성 중",
        "critique": "익명 상호 비평 중",
        "final": "최종 종합 중",
        "done": "토론 완료",
        "error": "오류 발생",
    }
    order = ["initial", "critique", "final", "done"]
    stage_index = order.index(stage) if stage in order else -1
    steps = [
        ("독립 답변", "각 AI가 서로의 답을 보지 않고 분석합니다."),
        ("익명 상호 비평", "작성자를 숨긴 답변의 오류와 빈틈을 검토합니다."),
        ("최종 종합", "선택한 AI가 하나의 최종안을 작성합니다."),
    ]
    step_html = []
    for index, (title, copy) in enumerate(steps):
        state_class = " done" if stage_index > index else " active" if stage_index == index else ""
        state_text = "완료" if stage_index > index else "진행 중" if stage_index == index else "대기"
        step_html.append(
            f'<div class="timeline-step{state_class}"><b>{"✓" if stage_index > index else index + 1}</b>'
            f'<div><strong>{title}</strong><span>{copy}</span></div>'
            f'<span class="timeline-state">{state_text}</span></div>'
        )
    st.markdown(
        f'<div class="progress-card"><div class="progress-title"><b>◌</b><div>'
        f'<strong>{stage_labels[stage]}</strong><span>토론 엔진 상태</span></div></div>{"".join(step_html)}</div>',
        unsafe_allow_html=True,
    )
    st.progress({"idle": 0, "initial": 30, "critique": 65, "final": 88, "done": 100, "error": 0}[stage])

elif "결과" in page:
    render_result(st.session_state.result)

elif "기록" in page:
    page_heading("SESSION HISTORY", "토론 기록", "현재 브라우저 세션에 남아 있는 최근 토론입니다.")
    if not st.session_state.history:
        st.markdown('<div class="empty-card">저장된 토론이 없습니다.</div>', unsafe_allow_html=True)
    for index, item in enumerate(st.session_state.history):
        created = datetime.fromisoformat(item["created_at"]).astimezone()
        with st.expander(f'{item["question"][:70]} · {created:%Y-%m-%d %H:%M}'):
            st.markdown(item["final_answer"])
            if st.button("이 결과 열기", key=f"open_{item['id']}_{index}"):
                st.session_state.result = item
                st.success("결과 탭에서 확인할 수 있습니다.")
    if st.session_state.history and st.button("기록 전체 삭제"):
        st.session_state.history = []
        st.session_state.result = None
        st.rerun()

else:
    key_count = sum(bool(value) for value in st.session_state.api_keys.values())
    page_heading(
        "CONNECTIONS",
        "API 연결 설정",
        "키는 현재 Streamlit 세션 메모리에만 유지됩니다.",
        f"{key_count} / 3 연결",
    )
    settings_columns = st.columns(3, gap="medium")
    for column, provider in zip(settings_columns, PROVIDER_NAMES):
        meta = PROVIDER_META[provider]
        with column:
            with st.container(border=True):
                st.markdown(
                    f'<div class="provider-head" style="--provider:{meta["color"]}">'
                    f'<img src="{asset_data_uri(meta["icon"])}" alt=""><div>'
                    f'<strong>{PROVIDER_NAMES[provider]}</strong><span>{meta["label"]}</span></div></div>',
                    unsafe_allow_html=True,
                )
                new_key = st.text_input(
                    "API Key",
                    value=st.session_state.api_keys[provider],
                    type="password",
                    key=f"key_{provider}",
                    autocomplete="off",
                )
                new_model = st.text_input(
                    "모델",
                    value=st.session_state.models[provider],
                    key=f"model_{provider}",
                )
                st.session_state.api_keys[provider] = new_key
                st.session_state.models[provider] = new_model
    st.markdown(
        '<div class="security"><b>✓ 키 보관 정책</b><br>'
        '입력한 키는 각 제공사의 API 요청에만 사용하며 소스 코드, GitHub 저장소, 토론 기록에 저장하지 않습니다.</div>',
        unsafe_allow_html=True,
    )
