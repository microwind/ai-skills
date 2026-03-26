#!/usr/bin/env python3
"""
事务管理 - 数据库事务处理和ACID特性示例
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import time

class IsolationLevel(Enum):
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"

@dataclass
class TransactionResult:
    success: bool
    message: str
    affected_rows: int = 0
    error: Optional[str] = None

class DatabaseManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection_pool = []
        self.lock = threading.Lock()
        
    def initialize_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建账户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number VARCHAR(20) UNIQUE NOT NULL,
                balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account VARCHAR(20) NOT NULL,
                to_account VARCHAR(20) NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'pending',
                FOREIGN KEY (from_account) REFERENCES accounts(account_number),
                FOREIGN KEY (to_account) REFERENCES accounts(account_number)
            )
        ''')
        
        # 创建订单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_amount DECIMAL(15,2) NOT NULL,
                order_status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建库存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name VARCHAR(100) UNIQUE NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00
            )
        ''')
        
        conn.commit()
        conn.close()
        
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    @contextmanager
    def transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
        """事务上下文管理器"""
        with self.get_connection() as conn:
            try:
                conn.execute(f"PRAGMA isolation_level = {isolation_level.value}")
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

class TransactionManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def create_account(self, account_number: str, initial_balance: float) -> TransactionResult:
        """创建账户"""
        try:
            with self.db_manager.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO accounts (account_number, balance) VALUES (?, ?)",
                    (account_number, initial_balance)
                )
                affected_rows = cursor.rowcount
                
            return TransactionResult(
                success=True,
                message=f"账户 {account_number} 创建成功",
                affected_rows=affected_rows
            )
        except sqlite3.IntegrityError:
            return TransactionResult(
                success=False,
                message=f"账户 {account_number} 已存在",
                error="Duplicate account"
            )
        except Exception as e:
            return TransactionResult(
                success=False,
                message="创建账户失败",
                error=str(e)
            )
    
    def transfer_money(self, from_account: str, to_account: str, amount: float) -> TransactionResult:
        """转账操作 - 演示事务的原子性"""
        try:
            with self.db_manager.transaction() as conn:
                cursor = conn.cursor()
                
                # 检查转出账户余额
                cursor.execute(
                    "SELECT balance FROM accounts WHERE account_number = ?",
                    (from_account,)
                )
                from_balance = cursor.fetchone()
                
                if not from_balance or from_balance['balance'] < amount:
                    return TransactionResult(
                        success=False,
                        message="转出账户余额不足",
                        error="Insufficient balance"
                    )
                
                # 检查转入账户是否存在
                cursor.execute(
                    "SELECT id FROM accounts WHERE account_number = ?",
                    (to_account,)
                )
                to_account_exists = cursor.fetchone()
                
                if not to_account_exists:
                    return TransactionResult(
                        success=False,
                        message="转入账户不存在",
                        error="Account not found"
                    )
                
                # 执行转账操作
                # 1. 扣除转出账户金额
                cursor.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
                    (amount, from_account)
                )
                
                # 2. 增加转入账户金额
                cursor.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
                    (amount, to_account)
                )
                
                # 3. 记录交易历史
                cursor.execute(
                    "INSERT INTO transactions (from_account, to_account, amount, status) VALUES (?, ?, ?, 'completed')",
                    (from_account, to_account, amount)
                )
                
                affected_rows = cursor.rowcount
                
            return TransactionResult(
                success=True,
                message=f"成功转账 {amount} 元从 {from_account} 到 {to_account}",
                affected_rows=affected_rows
            )
            
        except Exception as e:
            return TransactionResult(
                success=False,
                message="转账失败",
                error=str(e)
            )
    
    def place_order(self, customer_id: int, product_name: str, quantity: int) -> TransactionResult:
        """下单操作 - 演示事务的一致性"""
        try:
            with self.db_manager.transaction() as conn:
                cursor = conn.cursor()
                
                # 检查库存
                cursor.execute(
                    "SELECT quantity, unit_price FROM inventory WHERE product_name = ?",
                    (product_name,)
                )
                inventory = cursor.fetchone()
                
                if not inventory:
                    return TransactionResult(
                        success=False,
                        message="商品不存在",
                        error="Product not found"
                    )
                
                if inventory['quantity'] < quantity:
                    return TransactionResult(
                        success=False,
                        message="库存不足",
                        error="Insufficient inventory"
                    )
                
                unit_price = inventory['unit_price']
                total_amount = unit_price * quantity
                
                # 创建订单
                cursor.execute(
                    "INSERT INTO orders (customer_id, product_name, quantity, unit_price, total_amount, order_status) VALUES (?, ?, ?, ?, ?, 'confirmed')",
                    (customer_id, product_name, quantity, unit_price, total_amount)
                )
                
                # 更新库存
                cursor.execute(
                    "UPDATE inventory SET quantity = quantity - ? WHERE product_name = ?",
                    (quantity, product_name)
                )
                
                affected_rows = cursor.rowcount
                
            return TransactionResult(
                success=True,
                message=f"订单创建成功，总金额: {total_amount} 元",
                affected_rows=affected_rows
            )
            
        except Exception as e:
            return TransactionResult(
                success=False,
                message="下单失败",
                error=str(e)
            )
    
    def batch_transfer(self, transfers: List[Tuple[str, str, float]]) -> List[TransactionResult]:
        """批量转账 - 演示事务的隔离性"""
        results = []
        
        try:
            with self.db_manager.transaction() as conn:
                cursor = conn.cursor()
                
                for from_account, to_account, amount in transfers:
                    # 检查余额
                    cursor.execute(
                        "SELECT balance FROM accounts WHERE account_number = ?",
                        (from_account,)
                    )
                    from_balance = cursor.fetchone()
                    
                    if not from_balance or from_balance['balance'] < amount:
                        results.append(TransactionResult(
                            success=False,
                            message=f"{from_account} 余额不足",
                            error="Insufficient balance"
                        ))
                        continue
                    
                    # 检查转入账户
                    cursor.execute(
                        "SELECT id FROM accounts WHERE account_number = ?",
                        (to_account,)
                    )
                    to_account_exists = cursor.fetchone()
                    
                    if not to_account_exists:
                        results.append(TransactionResult(
                            success=False,
                            message=f"{to_account} 账户不存在",
                            error="Account not found"
                        ))
                        continue
                    
                    # 执行转账
                    cursor.execute(
                        "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
                        (amount, from_account)
                    )
                    
                    cursor.execute(
                        "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
                        (amount, to_account)
                    )
                    
                    cursor.execute(
                        "INSERT INTO transactions (from_account, to_account, amount, status) VALUES (?, ?, ?, 'completed')",
                        (from_account, to_account, amount)
                    )
                    
                    results.append(TransactionResult(
                        success=True,
                        message=f"成功转账 {amount} 元",
                        affected_rows=3
                    ))
                
        except Exception as e:
            # 批量操作失败时回滚所有操作
            results = [TransactionResult(
                success=False,
                message="批量转账失败，所有操作已回滚",
                error=str(e)
            )] * len(transfers)
        
        return results
    
    def get_account_balance(self, account_number: str) -> Optional[float]:
        """查询账户余额"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT balance FROM accounts WHERE account_number = ?",
                    (account_number,)
                )
                result = cursor.fetchone()
                return result['balance'] if result else None
        except Exception:
            return None
    
    def get_transaction_history(self, account_number: str) -> List[dict]:
        """获取交易历史"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM transactions 
                    WHERE from_account = ? OR to_account = ?
                    ORDER BY transaction_time DESC
                ''', (account_number, account_number))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

def main():
    """演示事务管理功能"""
    print("数据库事务管理演示")
    print("=" * 50)
    
    # 初始化数据库和事务管理器
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    
    transaction_manager = TransactionManager(db_manager)
    
    # 创建测试账户
    print("\n1. 创建测试账户")
    print("-" * 30)
    
    accounts = [
        ("ACC001", 1000.00),
        ("ACC002", 500.00),
        ("ACC003", 2000.00)
    ]
    
    for account_number, balance in accounts:
        result = transaction_manager.create_account(account_number, balance)
        print(f"{result.message}")
    
    # 查询初始余额
    print("\n初始账户余额:")
    for account_number, _ in accounts:
        balance = transaction_manager.get_account_balance(account_number)
        print(f"  {account_number}: ¥{balance:.2f}")
    
    # 演示转账操作
    print("\n\n2. 转账操作演示")
    print("-" * 30)
    
    transfers = [
        ("ACC001", "ACC002", 200.00),
        ("ACC003", "ACC001", 300.00),
        ("ACC002", "ACC003", 100.00)
    ]
    
    for from_acc, to_acc, amount in transfers:
        result = transaction_manager.transfer_money(from_acc, to_acc, amount)
        print(f"{result.message}")
    
    # 查询转账后余额
    print("\n转账后账户余额:")
    for account_number, _ in accounts:
        balance = transaction_manager.get_account_balance(account_number)
        print(f"  {account_number}: ¥{balance:.2f}")
    
    # 演示批量转账
    print("\n\n3. 批量转账演示")
    print("-" * 30)
    
    batch_transfers = [
        ("ACC001", "ACC002", 50.00),
        ("ACC002", "ACC003", 30.00),
        ("ACC003", "ACC001", 20.00)
    ]
    
    results = transaction_manager.batch_transfer(batch_transfers)
    for i, result in enumerate(results):
        print(f"转账 {i+1}: {result.message}")
    
    # 查询批量转账后余额
    print("\n批量转账后账户余额:")
    for account_number, _ in accounts:
        balance = transaction_manager.get_account_balance(account_number)
        print(f"  {account_number}: ¥{balance:.2f}")
    
    # 演示失败转账
    print("\n\n4. 失败转账演示")
    print("-" * 30)
    
    # 余额不足的转账
    result = transaction_manager.transfer_money("ACC002", "ACC001", 1000.00)
    print(f"余额不足转账: {result.message}")
    
    # 不存在的账户转账
    result = transaction_manager.transfer_money("ACC001", "ACC999", 100.00)
    print(f"不存在账户转账: {result.message}")
    
    # 显示交易历史
    print("\n\n5. 交易历史记录")
    print("-" * 30)
    
    for account_number, _ in accounts:
        print(f"\n账户 {account_number} 的交易历史:")
        history = transaction_manager.get_transaction_history(account_number)
        for transaction in history[:3]:  # 只显示最近3笔
            print(f"  {transaction['transaction_time']}: "
                  f"{transaction['from_account']} → {transaction['to_account']} "
                  f"¥{transaction['amount']:.2f} ({transaction['status']})")

if __name__ == '__main__':
    main()
