# admin_app/app.py (修改后，将大部分代码封装在函数中)

import streamlit as st
import json
import os
from game_logic.models import Player, Market, GameSettings
from game_logic.calculations import calculate_round_results, get_ranked_players
import pandas as pd
from datetime import datetime

# --- 数据文件路径 ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PLAYERS_FILE = os.path.join(DATA_DIR, 'players.json')
MARKETS_FILE = os.path.join(DATA_DIR, 'market.json')
GAME_SETTINGS_FILE = os.path.join(DATA_DIR, 'game_settings.json')
ROUNDS_HISTORY_FILE = os.path.join(DATA_DIR, 'rounds_history.json')

# --- 数据加载与保存辅助函数 (保持不变) ---
def load_players_data():
    # ... (与之前相同)
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
    # ... (与之前相同)
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump([p.to_dict() for p in players], f, indent=4, ensure_ascii=False)

def load_markets_data():
    # ... (与之前相同)
    if not os.path.exists(MARKETS_FILE):
        return []
    try:
        with open(MARKETS_FILE, 'r', encoding='utf-8') as f:
            markets_data = json.load(f)
            return [Market.from_dict(m) for m in markets_data]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"加载市场数据出错: {e}")
        return []

def save_markets_data(markets: list[Market]):
    # ... (与之前相同)
    with open(MARKETS_FILE, 'w', encoding='utf-8') as f:
        json.dump([m.to_dict() for m in markets], f, indent=4, ensure_ascii=False)

def load_game_settings():
    # ... (与之前相同)
    if not os.path.exists(GAME_SETTINGS_FILE):
        default_settings = GameSettings()
        save_game_settings(default_settings)
        return default_settings
    try:
        with open(GAME_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
            return GameSettings.from_dict(settings_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"加载游戏设置出错: {e}")
        default_settings = GameSettings()
        save_game_settings(default_settings)
        return default_settings

def save_game_settings(settings: GameSettings):
    # ... (与之前相同)
    with open(GAME_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings.to_dict(), f, indent=4, ensure_ascii=False)

def save_round_history(round_data: dict):
    # ... (与之前相同)
    history = []
    if os.path.exists(ROUNDS_HISTORY_FILE):
        try:
            with open(ROUNDS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            st.warning("警告：历史数据文件损坏，将重新创建。")
            history = []
    
    history.append(round_data)
    with open(ROUNDS_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


# --- 核心管理员应用逻辑封装在函数中 ---
def admin_app_main():
    """
    管理员端应用的主函数。
    """
    st.set_page_config(layout="wide", page_title="商业模拟运营游戏 - 管理员端") # Streamlit 1.x 可以在函数内设置
    st.title("商业模拟运营游戏 - 管理员端")

    # 重新加载数据以确保最新状态
    current_players = load_players_data()
    current_markets = load_markets_data()
    current_game_settings = load_game_settings()

    if not current_players or not current_markets or not current_game_settings:
        st.warning("数据加载失败或文件不存在，请检查您的 'data' 文件夹并确保数据文件已初始化。")
        # st.stop() # 不再在这里停止，因为主应用会处理初始状态

    st.sidebar.subheader("游戏控制")
    st.sidebar.metric("当前游戏回合", current_markets[0].current_round if current_markets else "未设置")
    st.sidebar.metric("总回合数", current_game_settings.total_rounds)


    # --- 侧边栏导航 (管理员独有) ---
    admin_page_selection = st.sidebar.radio("管理员功能", ["游戏准备", "游戏运行与总览"])

    if admin_page_selection == "游戏准备":
        st.header("🎮 游戏开始前准备")

        # (1) 设置玩家数量和生成密码
        st.subheader("1. 玩家与密码设置")
        num_players_input = st.number_input("设置玩家数量:", min_value=1, value=len(current_players), step=1)
        
        if st.button("生成/更新玩家账户"):
            new_players_list = []
            for i in range(num_players_input):
                player_id = f"player{i+1}"
                existing_player = next((p for p in current_players if p.player_id == player_id), None)
                if existing_player:
                    new_players_list.append(existing_player)
                else:
                    new_players_list.append(Player(player_id=player_id, company_name=f"公司{i+1}", initial_capital=current_game_settings.initial_player_capital))
            
            save_players_data(new_players_list)
            st.success(f"已生成/更新 {num_players_input} 位玩家账户。")
            st.experimental_rerun()

        if current_players:
            st.markdown("---")
            st.write("### 玩家登录信息")
            player_login_data = []
            for p in current_players:
                player_login_data.append({
                    "玩家ID": p.player_id,
                    "公司名称": p.company_name,
                    "登录密码": p.password
                })
            st.dataframe(pd.DataFrame(player_login_data), hide_index=True)
            csv = pd.DataFrame(player_login_data).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="下载玩家登录信息 (CSV)",
                data=csv,
                file_name="player_login_info.csv",
                mime="text/csv",
            )
        else:
            st.info("请先设置玩家数量并生成账户。")


        st.markdown("---")
        # (2) 设置市场
        st.subheader("2. 市场设置")
        num_markets_input = st.number_input("设置市场数量:", min_value=1, value=len(current_markets) if current_markets else 1, step=1)

        market_configs = []
        for i in range(num_markets_input):
            st.write(f"#### 市场 {i+1} 设置")
            existing_market = current_markets[i] if i < len(current_markets) else None
            
            with st.expander(f"市场 {i+1} 详细设置", expanded=True):
                market_name = st.text_input(f"市场 {i+1} 名称:", value=existing_market.name if existing_market else f"城市{chr(65+i)}市场", key=f"market_name_{i}")
                total_market_size = st.number_input(f"市场 {i+1} 总需求量 (单位):", min_value=1000, value=existing_market.total_market_size if existing_market else 10000, step=100, key=f"market_size_{i}")
                base_material_cost = st.number_input(f"市场 {i+1} 基础材料成本 (每单位):", min_value=0.1, value=existing_market.base_material_cost if existing_market else 5.0, step=0.1, format="%.2f", key=f"material_cost_{i}")
                base_labor_cost = st.number_input(f"市场 {i+1} 基础人工工资 (每位员工):", min_value=1.0, value=existing_market.base_labor_cost if existing_market else 10.0, step=1.0, format="%.2f", key=f"labor_cost_{i}")
                loan_interest_rate = st.number_input(f"市场 {i+1} 贷款利率 (%):", min_value=0.1, max_value=20.0, value=existing_market.loan_interest_rate * 100 if existing_market else 5.0, step=0.1, format="%.1f", key=f"loan_rate_{i}") / 100
                initial_avg_price = st.number_input(f"市场 {i+1} 初始平均价格:", min_value=1.0, value=existing_market.initial_avg_price if existing_market else 20.0, step=0.1, format="%.2f", key=f"avg_price_{i}")

                market_configs.append(Market(
                    name=market_name,
                    total_market_size=total_market_size,
                    base_material_cost=base_material_cost,
                    base_labor_cost=base_labor_cost,
                    loan_interest_rate=loan_interest_rate,
                    initial_avg_price=initial_avg_price,
                    current_round=existing_market.current_round if existing_market else 0
                ))
        
        if st.button("保存市场设置"):
            save_markets_data(market_configs)
            st.success("市场参数已更新！")
            st.experimental_rerun()


        st.markdown("---")
        # (3) 设置基础信息
        st.subheader("3. 基础游戏设置")
        with st.form("game_settings_form"):
            initial_player_capital = st.number_input("玩家初始资金 (¥):", min_value=1000.0, value=current_game_settings.initial_player_capital, step=1000.0, format="%.2f")
            engineer_efficiency = st.number_input("工程师效率 (一人一轮可生产货物数量):", min_value=1, value=current_game_settings.engineer_efficiency, step=1)
            city_report_cost = st.number_input("一张城市报表的价格 (¥):", min_value=100.0, value=current_game_settings.city_report_cost, step=100.0, format="%.2f")
            city_store_cost = st.number_input("一个城市店铺的费用 (¥):", min_value=100.0, value=current_game_settings.city_store_cost, step=100.0, format="%.2f")
            min_product_price = st.number_input("玩家产品最低价 (¥):", min_value=0.1, value=current_game_settings.min_product_price, step=0.1, format="%.2f")
            max_product_price = st.number_input("玩家产品最高价 (¥):", min_value=0.1, value=current_game_settings.max_product_price, step=0.1, format="%.2f")
            total_rounds = st.number_input("游戏总回合数:", min_value=1, value=current_game_settings.total_rounds, step=1)

            settings_submitted = st.form_submit_button("保存基础游戏设置")
            if settings_submitted:
                updated_settings = GameSettings(
                    initial_player_capital=initial_player_capital,
                    engineer_efficiency=engineer_efficiency,
                    city_report_cost=city_report_cost,
                    city_store_cost=city_store_cost,
                    min_product_price=min_product_price,
                    max_product_price=max_product_price,
                    total_rounds=total_rounds
                )
                save_game_settings(updated_settings)
                st.success("基础游戏设置已更新！")
                st.experimental_rerun()

        st.markdown("---")
        st.header("KDS (Key Data Sheet) 页面")
        st.write("以下是当前游戏的关键数据汇总，您可以将其作为游戏规则文件发送给玩家。")

        # KDS 表格生成
        st.subheader("市场关键数据")
        market_data_for_display = []
        for m in current_markets:
            market_data_for_display.append({
                "市场名称": m.name,
                "市场总需求量": f"{m.total_market_size:,} 单位",
                "基础材料成本": f"¥{m.base_material_cost:,.2f}",
                "基础人工工资": f"¥{m.base_labor_cost:,.2f}",
                "市场贷款利率": f"{m.loan_interest_rate*100:.1f}%",
                "初始平均价格": f"¥{m.initial_avg_price:,.2f}"
            })
        st.dataframe(pd.DataFrame(market_data_for_display), hide_index=True, use_container_width=True)

        st.subheader("基础游戏规则")
        game_settings_data_for_display = pd.DataFrame([
            {"项目": "玩家初始资金", "数值": f"¥{current_game_settings.initial_player_capital:,.2f}"},
            {"项目": "工程师效率", "数值": f"{current_game_settings.engineer_efficiency} 货物/人/轮"},
            {"项目": "城市报表价格", "数值": f"¥{current_game_settings.city_report_cost:,.2f}"},
            {"项目": "城市店铺费用", "数值": f"¥{current_game_settings.city_store_cost:,.2f}"},
            {"项目": "产品最低价", "数值": f"¥{current_game_settings.min_product_price:,.2f}"},
            {"项目": "产品最高价", "数值": f"¥{current_game_settings.max_product_price:,.2f}"},
            {"项目": "游戏总回合数", "数值": f"{current_game_settings.total_rounds} 轮"}
        ])
        st.dataframe(game_settings_data_for_display, hide_index=True, use_container_width=True)
        st.warning("PDF生成功能将在后续版本中实现。目前您可以复制粘贴或使用浏览器打印功能。")


    elif admin_page_selection == "游戏运行与总览":
        st.header("➡️ 推进回合")
        st.warning("请确保所有玩家已提交本回合决策，再推进下一回合！")

        if st.button("推进下一回合"):
            st.info("正在计算本回合结果...")
            
            main_market = current_markets[0] if current_markets else None
            if not main_market:
                st.error("无法推进回合：未设置任何市场数据。")
                # st.stop() # 不在这里停止
                return # 退出函数，避免后续错误

            # Placeholder for actual calculation logic from game_logic/calculations.py
            # This needs to be implemented fully in Stage 2
            # For now, just advance round and save
            
            # TODO: Integrate the full Stage 2 calculation logic here!
            # Example: updated_players, updated_markets = calculate_round_results(current_players, current_markets, current_game_settings)
            # For now, just a dummy increment:
            main_market.current_round += 1 # Only update the main market's round
            
            save_players_data(current_players) # Save player decisions (they're already updated by players)
            save_markets_data(current_markets) # Save updated market data (including round increment)

            # Record round history (needs to be more detailed after calculations)
            round_history_data = {
                "round": main_market.current_round,
                "market_params": [m.to_dict() for m in current_markets],
                "player_states": [p.to_dict() for p in current_players]
            }
            save_round_history(round_history_data)

            st.success(f"回合 {main_market.current_round} 已成功推进！")
            st.experimental_rerun()

        st.markdown("---")
        # --- 玩家总览 ---
        st.header("📋 玩家总览")
        if current_players:
            # get_ranked_players needs to be updated to work with new Player model attributes
            ranked_players_for_display = get_ranked_players(current_players)
            overview_data = []
            for i, p in enumerate(ranked_players_for_display):
                overview_data.append({
                    "排名": i + 1,
                    "公司名称": p.company_name,
                    "ID": p.player_id,
                    "当前资金": f"¥{p.capital:,.2f}",
                    "净资产": f"¥{p.net_asset:,.2f}",
                    "贷款总额": f"¥{p.debt:,.2f}",
                    "上一回合利润": f"¥{p.last_round_profit:,.2f}",
                    "总市场份额": f"{p.market_share:.2%}"
                })
            st.dataframe(pd.DataFrame(overview_data), use_container_width=True, hide_index=True)
        else:
            st.info("暂无玩家数据。请在 '游戏准备' 页面设置玩家。")

        st.markdown("---")
        st.header("⚠️ 危险操作")
        if st.button("重置游戏数据 (请谨慎操作！)", help="这将清空所有玩家数据、市场数据和历史记录，并重置游戏到初始状态。"):
            if st.checkbox("我确认要重置游戏数据", key="reset_confirm_checkbox"):
                initial_players_data_raw = [{"player_id": f"player{i+1}", "company_name": f"公司{i+1}"} for i in range(2)]
                initial_players_objects = [Player(p['player_id'], p['company_name'], initial_capital=current_game_settings.initial_player_capital) for p in initial_players_data_raw]
                
                initial_markets_data_raw = [
                    {"name": "城市A市场", "total_market_size": 10000, "base_material_cost": 5.0, "base_labor_cost": 10.0, "loan_interest_rate": 0.05, "initial_avg_price": 20.0, "current_round": 0},
                    {"name": "城市B市场", "total_market_size": 8000, "base_material_cost": 5.5, "base_labor_cost": 11.0, "loan_interest_rate": 0.06, "initial_avg_price": 22.0, "current_round": 0}
                ]
                initial_markets_objects = [Market(**m) for m in initial_markets_data_raw]

                save_players_data(initial_players_objects)
                save_markets_data(initial_markets_objects)
                save_game_settings(GameSettings())

                if os.path.exists(ROUNDS_HISTORY_FILE):
                    os.remove(ROUNDS_HISTORY_FILE)
                
                st.success("游戏数据已重置！请刷新页面。")
                st.experimental_rerun()
            else:
                st.info("请勾选确认框以进行重置操作。")

# 如果这个文件被直接运行，则执行
if __name__ == "__main__":
    # 提示：此文件应通过主应用（main_app.py）运行
    st.warning("此文件应通过主应用（main_app.py）运行。")
    # 可以添加一个简单的管理员密码验证，以防直接运行
    # if st.text_input("管理员密码:", type="password") == "admin_password": # 例如
    #    admin_app_main()
