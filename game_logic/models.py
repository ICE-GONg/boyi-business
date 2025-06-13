# game_logic/models.py

import random
import string

class Player:
    def __init__(self, player_id: str, company_name: str, initial_capital: float = 100000, password: str = None):
        self.player_id = player_id
        self.company_name = company_name
        self.password = password if password else self._generate_password() # 新增密码
        self.capital = initial_capital
        self.debt = 0 # 新增贷款
        self.production_capacity = 1000 # 初始生产能力
        self.employees = 10 # 初始员工数
        self.product_quality = 5 # 初始产品质量 (1-10)

        # 玩家决策 (存储玩家输入的原始决策)
        self.current_production_plan = 0
        self.current_price = 0
        self.current_advertising_budget = 0
        self.current_performance_investment = 0 # 新增性能投资
        self.current_welfare_investment = 0 # 新增福利投资
        self.current_new_stores = {} # 新增城市店铺数量 {city_name: count}
        self.current_loan_amount = 0 # 新增本轮贷款申请额
        self.current_repay_loan_amount = 0 # 新增本轮还款额
        self.main_city = "" # 主场城市

        # 实际执行的投资 (经过资金/效率判断后的实际扣款和产量)
        self.actual_production = 0
        self.actual_advertising_investment = 0
        self.actual_performance_investment = 0
        self.actual_welfare_investment = 0
        self.actual_new_stores_cost = 0

        # 运营报表数据 (每回合更新)
        self.last_round_revenue = 0
        self.last_round_costs = 0
        self.last_round_profit = 0
        self.net_asset = initial_capital # 净资产 = 资金 - 负债

        self.market_share = 0 # 总市场份额
        self.cpi_per_city = {} # 每城市的CPI {city_name: cpi_value}
        self.hidden_cpi_per_city = {} # 每城市的隐藏CPI (管理员可见)
        self.actual_sales_per_city = {} # 每城市的实际销售量
        self.surplus_goods = 0 # 剩余货物

        # 报表购买状态 (存储玩家是否购买了城市报表)
        self.bought_city_reports = {} # {city_name: True/False}

    def _generate_password(self):
        """生成一个8位包含大小写字母和数字的随机密码"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(8))

    def to_dict(self):
        # 方便保存到文件或数据库
        return {
            "player_id": self.player_id,
            "company_name": self.company_name,
            "password": self.password, # 保存密码
            "capital": self.capital,
            "debt": self.debt,
            "production_capacity": self.production_capacity,
            "employees": self.employees,
            "product_quality": self.product_quality,
            "current_production_plan": self.current_production_plan,
            "current_price": self.current_price,
            "current_advertising_budget": self.current_advertising_budget,
            "current_performance_investment": self.current_performance_investment,
            "current_welfare_investment": self.current_welfare_investment,
            "current_new_stores": self.current_new_stores,
            "current_loan_amount": self.current_loan_amount,
            "current_repay_loan_amount": self.current_repay_loan_amount,
            "main_city": self.main_city,
            "actual_production": self.actual_production,
            "actual_advertising_investment": self.actual_advertising_investment,
            "actual_performance_investment": self.actual_performance_investment,
            "actual_welfare_investment": self.actual_welfare_investment,
            "actual_new_stores_cost": self.actual_new_stores_cost,
            "last_round_revenue": self.last_round_revenue,
            "last_round_costs": self.last_round_costs,
            "last_round_profit": self.last_round_profit,
            "net_asset": self.net_asset,
            "market_share": self.market_share,
            "cpi_per_city": self.cpi_per_city,
            "hidden_cpi_per_city": self.hidden_cpi_per_city,
            "actual_sales_per_city": self.actual_sales_per_city,
            "surplus_goods": self.surplus_goods,
            "bought_city_reports": self.bought_city_reports
        }

    @classmethod
    def from_dict(cls, data: dict):
        player = cls(
            player_id=data['player_id'],
            company_name=data['company_name'],
            initial_capital=data.get('capital', 100000),
            password=data.get('password') # 从数据加载密码
        )
        # 更新其他属性，使用 .get() 避免旧数据没有新字段时出错
        player.capital = data.get('capital', player.capital)
        player.debt = data.get('debt', player.debt)
        player.production_capacity = data.get('production_capacity', player.production_capacity)
        player.employees = data.get('employees', player.employees)
        player.product_quality = data.get('product_quality', player.product_quality)
        player.current_production_plan = data.get('current_production_plan', player.current_production_plan)
        player.current_price = data.get('current_price', player.current_price)
        player.current_advertising_budget = data.get('current_advertising_budget', player.current_advertising_budget)
        player.current_performance_investment = data.get('current_performance_investment', 0)
        player.current_welfare_investment = data.get('current_welfare_investment', 0)
        player.current_new_stores = data.get('current_new_stores', {})
        player.current_loan_amount = data.get('current_loan_amount', 0)
        player.current_repay_loan_amount = data.get('current_repay_loan_amount', 0)
        player.main_city = data.get('main_city', "")
        
        player.actual_production = data.get('actual_production', 0)
        player.actual_advertising_investment = data.get('actual_advertising_investment', 0)
        player.actual_performance_investment = data.get('actual_performance_investment', 0)
        player.actual_welfare_investment = data.get('actual_welfare_investment', 0)
        player.actual_new_stores_cost = data.get('actual_new_stores_cost', 0)

        player.last_round_revenue = data.get('last_round_revenue', 0)
        player.last_round_costs = data.get('last_round_costs', 0)
        player.last_round_profit = data.get('last_round_profit', 0)
        player.net_asset = data.get('net_asset', player.capital) # 初始化为capital，后续计算
        
        player.market_share = data.get('market_share', 0)
        player.cpi_per_city = data.get('cpi_per_city', {})
        player.hidden_cpi_per_city = data.get('hidden_cpi_per_city', {})
        player.actual_sales_per_city = data.get('actual_sales_per_city', {})
        player.surplus_goods = data.get('surplus_goods', 0)

        player.bought_city_reports = data.get('bought_city_reports', {})
        return player


class Market:
    def __init__(self, name: str = "默认市场", total_market_size: int = 10000, base_material_cost: float = 5,
                 base_labor_cost: float = 10, loan_interest_rate: float = 0.05, initial_avg_price: float = 20):
        self.name = name # 市场名称
        self.total_market_size = total_market_size # 市场总需求量
        self.base_material_cost = base_material_cost # 每单位产品材料成本
        self.base_labor_cost = base_labor_cost # 每个员工的基础工资
        self.loan_interest_rate = loan_interest_rate # 市场贷款利率
        self.initial_avg_price = initial_avg_price # 初始平均价格
        self.current_round = 0

    def to_dict(self):
        return {
            "name": self.name,
            "total_market_size": self.total_market_size,
            "base_material_cost": self.base_material_cost,
            "base_labor_cost": self.base_labor_cost,
            "loan_interest_rate": self.loan_interest_rate,
            "initial_avg_price": self.initial_avg_price,
            "current_round": self.current_round
        }

    @classmethod
    def from_dict(cls, data: dict):
        market = cls(
            name=data.get('name', "默认市场"),
            total_market_size=data['total_market_size'],
            base_material_cost=data['base_material_cost'],
            base_labor_cost=data['base_labor_cost'],
            loan_interest_rate=data.get('loan_interest_rate', 0.05), # 新增默认值
            initial_avg_price=data.get('initial_avg_price', 20) # 新增默认值
        )
        market.current_round = data.get('current_round', 0)
        return market

# 新增一个类来存储基础游戏设置
class GameSettings:
    def __init__(self, initial_player_capital: float = 100000, engineer_efficiency: int = 40,
                 city_report_cost: float = 5000, city_store_cost: float = 10000,
                 min_product_price: float = 1.0, max_product_price: float = 100.0, total_rounds: int = 10):
        self.initial_player_capital = initial_player_capital
        self.engineer_efficiency = engineer_efficiency # 一个人一轮可以做多少货物
        self.city_report_cost = city_report_cost # 一张城市报表的价格
        self.city_store_cost = city_store_cost # 一个城市店铺的费用
        self.min_product_price = min_product_price # 玩家卖产品的最低价
        self.max_product_price = max_product_price # 玩家卖产品的最高价
        self.total_rounds = total_rounds # 总轮数

    def to_dict(self):
        return {
            "initial_player_capital": self.initial_player_capital,
            "engineer_efficiency": self.engineer_efficiency,
            "city_report_cost": self.city_report_cost,
            "city_store_cost": self.city_store_cost,
            "min_product_price": self.min_product_price,
            "max_product_price": self.max_product_price,
            "total_rounds": self.total_rounds
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            initial_player_capital=data.get('initial_player_capital', 100000),
            engineer_efficiency=data.get('engineer_efficiency', 40),
            city_report_cost=data.get('city_report_cost', 5000),
            city_store_cost=data.get('city_store_cost', 10000),
            min_product_price=data.get('min_product_price', 1.0),
            max_product_price=data.get('max_product_price', 100.0),
            total_rounds=data.get('total_rounds', 10)
        )
