import random
import textwrap

import streamlit as st

st.set_page_config(
    page_title="Python Study Sprint",
    page_icon="🐍",
    layout="wide",
)

LESSONS = [
    {
        "title": "変数とデータ型",
        "level": "初級",
        "summary": "文字列・数値・真偽値・リストなど、Pythonで頻出する基本の型を学びます。",
        "points": [
            "変数は = で代入する",
            "型を確認するときは type() を使う",
            "list や dict は複数データをまとめるのに便利",
        ],
        "sample": "name = 'Sakura'\nage = 12\nprint(type(name), type(age))",
    },
    {
        "title": "条件分岐",
        "level": "初級",
        "summary": "if / elif / else を使って、条件ごとに処理を分ける方法を学びます。",
        "points": [
            "条件式は True / False を返す",
            "比較演算子には ==, !=, >, < がある",
            "インデントでブロックを表現する",
        ],
        "sample": "score = 82\nif score >= 80:\n    print('Great!')\nelse:\n    print('Keep going!')",
    },
    {
        "title": "繰り返し",
        "level": "中級",
        "summary": "for / while を使って、同じ処理を効率よく繰り返す考え方を学びます。",
        "points": [
            "for はコレクションの走査に向く",
            "while は条件が成り立つ間だけ繰り返す",
            "break と continue でループ制御ができる",
        ],
        "sample": "for number in range(1, 4):\n    print(number)",
    },
    {
        "title": "関数",
        "level": "中級",
        "summary": "def を使って、処理を再利用しやすい単位に分割します。",
        "points": [
            "関数名は動詞ベースにすると分かりやすい",
            "引数で入力を受け取り、return で結果を返す",
            "小さく分けるとテストしやすい",
        ],
        "sample": "def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Python'))",
    },
]

QUIZZES = [
    {
        "question": "リストの長さを取得する組み込み関数はどれですか？",
        "choices": ["count()", "size()", "len()", "length()"],
        "answer": "len()",
        "explanation": "Pythonでは list や string の長さを len() で取得します。",
    },
    {
        "question": "条件分岐で『等しい』を比較するときに使う演算子は？",
        "choices": ["=", "==", ":=", "!="],
        "answer": "==",
        "explanation": "= は代入、== は値の比較です。",
    },
    {
        "question": "関数を定義するときに使うキーワードは？",
        "choices": ["func", "define", "def", "lambda"],
        "answer": "def",
        "explanation": "通常の関数定義は def で始めます。",
    },
]

PRACTICE_PROMPTS = [
    "1から10までの偶数だけを表示するコードを書いてみましょう。",
    "辞書型を使って、名前と年齢を持つプロフィールを表現してみましょう。",
    "数値のリストを受け取り、合計値を返す関数を作ってみましょう。",
    "ユーザーの点数に応じてメッセージを変える if 文を書いてみましょう。",
]

ROADMAP = [
    ("Week 1", "変数・型・print関数に慣れる"),
    ("Week 2", "if文とfor文でロジックを組み立てる"),
    ("Week 3", "関数化してコードを再利用する"),
    ("Week 4", "小さなCLIアプリを1本完成させる"),
]

if "progress" not in st.session_state:
    st.session_state.progress = {lesson["title"]: False for lesson in LESSONS}

if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = {}

st.title("🐍 Python Study Sprint")
st.caption("Pythonの基礎を、レッスン・クイズ・実践課題の3ステップで学ぶミニ学習アプリ")

col1, col2, col3 = st.columns(3)
completed_lessons = sum(st.session_state.progress.values())
quiz_correct = sum(1 for result in st.session_state.quiz_results.values() if result)
progress_rate = int((completed_lessons + quiz_correct) / (len(LESSONS) + len(QUIZZES)) * 100)

col1.metric("完了レッスン", f"{completed_lessons}/{len(LESSONS)}")
col2.metric("正解クイズ", f"{quiz_correct}/{len(QUIZZES)}")
col3.metric("総合進捗", f"{progress_rate}%")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["レッスン", "クイズ", "実践", "学習ロードマップ"])

with tab1:
    st.subheader("基礎を短く学ぶ")
    for lesson in LESSONS:
        with st.container(border=True):
            left, right = st.columns([3, 2])
            with left:
                st.markdown(f"### {lesson['title']}  ")
                st.write(f"**難易度:** {lesson['level']}")
                st.write(lesson["summary"])
                st.markdown("**学習ポイント**")
                for point in lesson["points"]:
                    st.markdown(f"- {point}")
            with right:
                st.code(lesson["sample"], language="python")
                checked = st.checkbox(
                    f"『{lesson['title']}』を学習済みにする",
                    value=st.session_state.progress[lesson["title"]],
                    key=f"lesson-{lesson['title']}",
                )
                st.session_state.progress[lesson["title"]] = checked

with tab2:
    st.subheader("理解度チェック")
    for index, quiz in enumerate(QUIZZES):
        with st.container(border=True):
            st.markdown(f"**Q{index + 1}. {quiz['question']}**")
            selected = st.radio(
                "回答を選んでください",
                options=quiz["choices"],
                key=f"quiz-{index}",
                index=None,
            )
            if st.button("答え合わせ", key=f"check-{index}"):
                is_correct = selected == quiz["answer"]
                st.session_state.quiz_results[index] = is_correct
                if is_correct:
                    st.success("正解です！")
                else:
                    st.error(f"不正解です。正解は {quiz['answer']} です。")
                st.info(quiz["explanation"])

with tab3:
    st.subheader("今日の実践メニュー")
    prompt = st.session_state.get("prompt") or random.choice(PRACTICE_PROMPTS)
    st.session_state.prompt = prompt
    st.info(prompt)
    notes = st.text_area(
        "学んだことや、自分で書いたコードのポイントをメモしましょう。",
        height=180,
        placeholder="例: for文とif文を組み合わせて偶数だけ表示できた。次は関数にまとめたい。",
    )
    if st.button("別の課題にする"):
        choices = [item for item in PRACTICE_PROMPTS if item != st.session_state.prompt]
        st.session_state.prompt = random.choice(choices)
        st.rerun()

    if notes:
        st.success("メモを残しました。学習内容を言語化すると定着しやすくなります。")
        st.markdown("#### 振り返りのヒント")
        st.write(
            textwrap.dedent(
                """
                - どの文法を使ったか
                - どこでつまずいたか
                - 次に改善したいこと
                """
            )
        )

with tab4:
    st.subheader("4週間のおすすめ学習プラン")
    for week, description in ROADMAP:
        st.markdown(f"- **{week}**: {description}")

    st.markdown("#### 次に作ってみると良い作品")
    st.write(
        "じゃんけんゲーム、ToDo CLI、簡単な家計簿、タイピング記録ツールなど、"
        "小さく完成できる作品から始めるのがおすすめです。"
    )

st.divider()
st.markdown("### 学習のコツ")
st.write(
    "毎日10〜15分でもコードを書く習慣をつけると、Pythonの文法と考え方が定着しやすくなります。"
)
