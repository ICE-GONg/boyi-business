# main_app.py
import streamlit as st
import json
import os
from game_logic.models import Player # 需要Player类来验证玩家
# 导入封装好的玩家和管理员应用主函数
from player_app.app import player_app_main, load_players_data, load_markets_data, load_game_settings
from admin_app.app import admin_app_main, load_players_data as admin_load_players_data # 避免名称冲突

# 定义管理员的硬编码密码 (在实际应用中，这应该更安全地存储)
ADMIN_PASSWORD = "adminpass" # 您可以设置一个您自己的管理员密码

# Streamlit session state 用于存储登录状态和当前用户
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None # 'player' or 'admin'
if 'current_player_obj' not in st.session_state:
    st.session_state['current_player_obj'] = None


# --- 登录界面函数 ---
def login_page():
    st.set_page_config(layout="centered", page_title="商业模拟运营游戏 - 登录")
    st.title("欢迎来到商业模拟运营游戏")
    st.subheader("请登录以继续")

    players = load_players_data() # 加载玩家数据用于验证

    if not players:
        st.warning("系统尚未初始化玩家数据。请联系管理员进行设置。")
        st.info("如果您是管理员，可以通过输入管理员密码直接进入管理员界面。")
        st.markdown("---") # 分割线

    login_type = st.radio("选择登录类型:", ["玩家登录", "管理员登录"])

    if login_type == "玩家登录":
        player_id = st.text_input("玩家ID:")
        password = st.text_input("密码:", type="password")
        login_button = st.button("玩家登录")

        if login_button:
            found_player = None
            for p in players:
                if p.player_id == player_id and p.password == password:
                    found_player = p
                    break
            
            if found_player:
                st.session_state['logged_in'] = True
                st.session_state['user_type'] = 'player'
                st.session_state['current_player_obj'] = found_player
                st.success(f"玩家 {found_player.company_name} 登录成功！")
                st.experimental_rerun() # 重新运行整个应用以显示玩家界面
            else:
                st.error("玩家ID或密码不正确。")

    elif login_type == "管理员登录":
        admin_password_input = st.text_input("管理员密码:", type="password", key="admin_pass_input")
        admin_login_button = st.button("管理员登录")

        if admin_login_button:
            if admin_password_input == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.session_state['user_type'] = 'admin'
                st.success("管理员登录成功！")
                st.experimental_rerun() # 重新运行整个应用以显示管理员界面
            else:
                st.error("管理员密码不正确。")

# --- 应用主逻辑 ---
def main():
    if not st.session_state['logged_in']:
        login_page()
    else:
        # 在侧边栏提供登出按钮
        if st.sidebar.button("退出登录"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.session_state['current_player_obj'] = None
            st.experimental_rerun() # 重新运行以显示登录页

        if st.session_state['user_type'] == 'player':
            # 确保传递给玩家应用的 player 对象是最新加载的
            # 由于 Streamlit 每次 rerun 都会从头运行脚本，
            # 我们需要确保 player_app_main 拿到的 current_player_obj 是最新的数据
            updated_players = load_players_data()
            current_player_id = st.session_state['current_player_obj'].player_id
            current_player_obj = next((p for p in updated_players if p.player_id == current_player_id), None)
            
            if current_player_obj:
                player_app_main(current_player_obj)
            else:
                st.error("无法加载您的玩家数据，请重新登录。")
                # 强制登出
                st.session_state['logged_in'] = False
                st.session_state['user_type'] = None
                st.session_state['current_player_obj'] = None
                st.experimental_rerun()

        elif st.session_state['user_type'] == 'admin':
            admin_app_main()

# 运行主应用
if __name__ == "__main__":
    main()
