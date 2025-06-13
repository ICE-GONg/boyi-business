# player_app/app.py

import streamlit as st
import json
import os
from game_logic.models import Player, Market, GameSettings # 引入 GameSettings
from game_logic.calculations import get_ranked_players # get_ranked_players 可能需要调整以适应新模型
import pandas as pd

# --- 数据文件路径 ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')
MARKETS_FILE = os.path.join(DATA_DIR, 'market.json') # 注意这里是 MARKETS_FILE
GAME_SETTINGS_FILE = os.path.join(DATA_DIR, 'game_settings.json') # 新增游戏设置文件路径

# --- 数据加载辅助函数 ---
def load_players_data():
    """加载玩家数据。"""
    if not os.path.exists(PLAYERS_FILE):
        return []
    try:
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            players_data = json.load(f)
            return [Player.from_dict(p) for p in players_data]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"加载玩家数据出错: {e}")
        return []

def save_players_data(players: list[Player]):
    """保存玩家数据。"""
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump([p.to_dict() for p in players], f, indent=4, ensure_ascii=False)

def load_markets_data():
    """加载市场数据。"""
    if not os.path.exists(MARKETS_FILE):
        return []
    try:
        with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
            markets_data = json.load(f)
            return [Market.from_dict(m) for m in markets_data]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"加载市场数据出错: {e}")
        return []

def load_game_settings():
    """加载游戏设置。"""
    if not os.path.exists(GAME_SETTINGS_FILE):
        return GameSettings() # 返回默认设置
    try:
        with open(GAME_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
            return GameSettings.from_dict(settings_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"加载游戏设置出错: {e}")
        return GameSettings()

# --- Streamlit 页面配置 ---
st.set_page_config(layout="wide", page_title="商业模拟运营游戏 - 玩家端")
st.title("商业模拟运营游戏 - 玩家端")

# --- 加载所有数据 ---
players = load_players_data()
markets = load_markets_data() # 加载所有市场
game_settings = load_game_settings() # 加载游戏设置

if not players or not markets or not game_settings:
    st.warning("数据加载失败或文件不存在，请检查您的 'data' 文件夹。请联系管理员初始化游戏。")
    st.stop() # 停止运行 Streamlit 应用

# 简单的玩家登录/选择 (现在有密码了)
st.sidebar.subheader("玩家登录")
player_id_input = st.sidebar.text_input("请输入您的玩家ID (例如: player1):")
password_input = st.sidebar.text_input("请输入您的密码:", type="password")

current_player = None
if player_id_input and password_input:
    for p in players:
        if p.player_id == player_id_input and p.password == password_input:
            current_player = p
            break
    if current_player is None:
        st.sidebar.error("玩家ID或密码不正确。")
else:
    st.sidebar.info("请输入您的玩家ID和密码登录。")

if current_player is None:
    st.stop() # 未登录则停止显示后续内容

st.sidebar.subheader(f"欢迎您，{current_player.company_name}！")
st.sidebar.metric("当前资金", f"¥{current_player.capital:,.2f}")
st.sidebar.metric("净资产", f"¥{current_player.net_asset:,.2f}")
st.sidebar.metric("当前回合", markets[0].current_round if markets else "N/A") # 显示第一个市场的回合数
st.sidebar.metric("剩余回合", game_settings.total_rounds - (markets[0].current_round if markets else 0))

# --- 决策界面 ---
st.header("⚙️ 决策中心")
with st.form("decision_form"):
    st.subheader("生产与销售决策")
    new_production_plan = st.number_input(
        "计划生产数量 (单位):",
        min_value=0,
        max_value=current_player.production_capacity, # 假设生产能力上限
        value=current_player.current_production_plan,
        step=100
    )
    new_price = st.number_input(
        f"产品定价 (每单位, ¥{game_settings.min_product_price:.2f}-¥{game_settings.max_product_price:.2f}):",
        min_value=game_settings.min_product_price,
        max_value=game_settings.max_product_price,
        value=current_player.current_price if current_player.current_price > 0 else game_settings.initial_avg_price, # 初始显示平均价格
        step=0.1,
        format="%.2f"
    )
    new_advertising_budget = st.number_input(
        "广告投入 (¥):",
        min_value=0,
        value=current_player.current_advertising_budget,
        step=100
    )

    st.subheader("投资与财务")
    new_performance_investment = st.number_input("性能投资 (¥):", min_value=0, value=current_player.current_performance_investment, step=100)
    new_welfare_investment = st.number_input("福利投资 (¥):", min_value=0, value=current_player.current_welfare_investment, step=100)
    
    st.write("#### 城市店铺投资")
    new_stores_data = {}
    for market_obj in markets:
        current_stores = current_player.current_new_stores.get(market_obj.name, 0)
        new_stores = st.number_input(
            f"在 {market_obj.name} 增设店铺数量 (每间费用: ¥{game_settings.city_store_cost:,.0f}):",
            min_value=0, value=current_stores, step=1, key=f"stores_{market_obj.name}"
        )
        new_stores_data[market_obj.name] = new_stores
    
    st.write("#### 贷款与还款")
    new_loan_amount = st.number_input("申请贷款 (¥):", min_value=0, value=current_player.current_loan_amount, step=1000)
    new_repay_loan_amount = st.number_input("偿还贷款 (¥):", min_value=0, max_value=int(current_player.debt), value=current_player.current_repay_loan_amount, step=1000)

    st.write("#### 主场城市选择")
    main_city_options = [""] + [m.name for m in markets] # 添加一个空选项
    selected_main_city = st.selectbox("选择您的主场城市 (用于计算贷款利息，且只能选择一个):", main_city_options, index=main_city_options.index(current_player.main_city) if current_player.main_city in main_city_options else 0)


    submitted = st.form_submit_button("提交本回合决策")

    if submitted:
        # 更新玩家决策
        current_player.current_production_plan = new_production_plan
        current_player.current_price = new_price
        current_player.current_advertising_budget = new_advertising_budget
        current_player.current_performance_investment = new_performance_investment
        current_player.current_welfare_investment = new_welfare_investment
        current_player.current_new_stores = new_stores_data
        current_player.current_loan_amount = new_loan_amount
        current_player.current_repay_loan_amount = new_repay_loan_amount
        current_player.main_city = selected_main_city
        
        # 实时保存决策（此处只保存玩家自己的决策，并不触发回合计算）
        # 回合计算应该由管理员端触发
        save_players_data(players) 
        st.success("您的决策已提交！请等待管理员推进下一回合。")

# --- 运营报表和信息 ---
st.markdown("---")
st.header("📊 运营报表")

col1, col2, col3, col4 = st.columns(4)
col1.metric("上一回合收入", f"¥{current_player.last_round_revenue:,.2f}")
col2.metric("上一回合成本", f"¥{current_player.last_round_costs:,.2f}")
col3.metric("上一回合利润", f"¥{current_player.last_round_profit:,.2f}")
col4.metric("您的总市场份额", f"{current_player.market_share:.2%}")

st.subheader("市场信息")
for market_obj in markets:
    st.write(f"#### {market_obj.name}")
    st.metric(f"{market_obj.name} - 总需求", market_obj.total_market_size)
    st.metric(f"{market_obj.name} - 您在该市场的CPI", f"{current_player.cpi_per_city.get(market_obj.name, 0):.2%}")
    st.metric(f"{market_obj.name} - 实际销售量", f"{current_player.actual_sales_per_city.get(market_obj.name, 0)} 单位")

st.metric("剩余未售货物", f"{current_player.surplus_goods} 单位")

# 显示资金排名
st.markdown("---")
st.header("🏆 资金排名")
ranked_players = get_ranked_players(players)
ranked_data = []
for i, p in enumerate(ranked_players):
    ranked_data.append({
        "排名": i + 1,
        "公司名称": p.company_name,
        "当前资金": f"¥{p.capital:,.2f}",
        "净资产": f"¥{p.net_asset:,.2f}",
        "上一回合利润": f"¥{p.last_round_profit:,.2f}",
        "总市场份额": f"{p.market_share:.2%}"
    })
st.dataframe(pd.DataFrame(ranked_data), hide_index=True)
