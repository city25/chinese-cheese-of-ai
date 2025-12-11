#!/usr/bin/env python3
"""后台训练脚本"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from datetime import datetime
from chess_core import ChineseChess, ChessAI
from chess_core.utils import get_cpu_usage, get_memory_usage, format_time

class SelfPlayTrainer:
    """自我对弈训练系统"""
    
    def __init__(self, ai1: ChessAI, ai2: ChessAI, output_file: str = None):
        self.ai1 = ai1
        self.ai2 = ai2
        self.output_file = output_file or f"data/training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.training_data = []
        self.game_stats = {
            'total_games': 0,
            'red_wins': 0,
            'black_wins': 0,
            'total_moves': 0,
            'total_time': 0,
            'start_time': time.time(),
            'benchmark': {}
        }
        
        # 创建数据目录
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
    def run_self_play(self, num_games: int = 100, max_moves: int = 150):
        """运行自我对弈"""
        print("="*80)
        print("中国象棋AI自我对弈训练系统")
        print(f"目标对局数: {num_games}")
        print(f"每局最大步数: {max_moves}")
        print(f"AI搜索深度: {self.ai1.search_depth}")
        print(f"输出文件: {self.output_file}")
        print("="*80)
        
        # 运行基准测试
        print("\n运行性能基准测试...")
        avg_time = self._benchmark_single_game()
        self.game_stats['benchmark']['avg_game_time'] = avg_time
        
        try:
            for game_id in range(1, num_games + 1):
                game_start = time.time()
                game_data = self._play_single_game(game_id, max_moves)
                game_duration = time.time() - game_start
                
                self.training_data.extend(game_data)
                self.game_stats['total_games'] += 1
                self.game_stats['total_moves'] += len(game_data)
                
                result = game_data[-1]['result'] if game_data else 'draw'
                if result == 'red':
                    self.game_stats['red_wins'] += 1
                elif result == 'black':
                    self.game_stats['black_wins'] += 1
                
                # 每10局保存一次
                if game_id % 10 == 0:
                    self._save_data()
                    self._print_progress(game_id, num_games, game_duration)
                
                # 休眠10ms释放CPU
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n检测到 Ctrl+C，正在保存数据...")
        
        finally:
            self.game_stats['total_time'] = time.time() - self.game_stats['start_time']
            self._save_data()
            self._print_final_stats()
        
    def _benchmark_single_game(self) -> float:
        """测试单局对弈时间"""
        times = []
        for _ in range(3):  # 测试3局取平均
            start = time.time()
            game = ChineseChess()
            for _ in range(10):  # 只下10步
                if game.game_over:
                    break
                ai = self.ai1 if game.current_player == 'red' else self.ai2
                move = ai.get_best_move(game)
                if move:
                    game.make_move(move)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        print(f"单局平均时间: {avg_time:.2f}秒")
        return avg_time
        
    def _play_single_game(self, game_id: int, max_moves: int) -> list:
        """单局对弈"""
        game = ChineseChess()
        game_data = []
        
        for move_count in range(1, max_moves + 1):
            current_ai = self.ai1 if game.current_player == 'red' else self.ai2
            
            # 记录当前状态
            board_state = game.get_board_state().tolist()
            
            # AI选择走法
            move = current_ai.get_best_move(game)
            if not move:
                break
            
            # 执行走法
            game.make_move(move)
            
            # 记录数据
            game_data.append({
                'game_id': game_id,
                'move_number': move_count,
                'player': game.current_player,
                'board_state': board_state,
                'move': move,
                'piece_type': abs(game.board[move[2], move[3]]),
                'captured_piece': abs(game.board[move[2], move[3]]) if game.board[move[2], move[3]] != 0 else 0
            })
            
            if game.game_over:
                break
        
        # 添加结果
        result = game.winner if game.winner else 'draw'
        for record in game_data:
            record['result'] = result
        
        return game_data
    
    def _save_data(self):
        """保存训练数据"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_data, f, ensure_ascii=False, indent=2)
        
        with open("data/stats.json", 'w', encoding='utf-8') as f:
            json.dump(self.game_stats, f, ensure_ascii=False, indent=2)
            
        # 保存AI统计
        ai1_stats = self.ai1.get_stats()
        ai2_stats = self.ai2.get_stats()
        with open("data/ai_stats.json", 'w', encoding='utf-8') as f:
            json.dump({'ai1': ai1_stats, 'ai2': ai2_stats}, f, indent=2)
        
        # AI缓存清理
        if self.ai1._transposition_table:
            self.ai1._transposition_table.clear()
        if self.ai2._transposition_table:
            self.ai2._transposition_table.clear()
    
    def _print_progress(self, current: int, total: int, last_game_time: float):
        """打印进度"""
        cpu_usage = get_cpu_usage()
        mem_usage = get_memory_usage()
        
        print(f"\n{'='*80}")
        print(f"进度: {current}/{total} ({current/total*100:.1f}%)")
        print(f"最近一局: {last_game_time:.2f}秒")
        print(f"总时长: {format_time(time.time() - self.game_stats['start_time'])}")
        print(f"红方胜率: {self.game_stats['red_wins']/current*100:.1f}%")
        print(f"黑方胜率: {self.game_stats['black_wins']/current*100:.1f}%")
        print(f"CPU使用率: {cpu_usage:.1f}%")
        print(f"内存使用: {mem_usage:.1f} MB")
        print(f"数据点数: {len(self.training_data)}")
        print(f"{'='*80}\n")
    
    def _print_final_stats(self):
        """打印最终统计"""
        total_games = self.game_stats['total_games']
        total_time = self.game_stats['total_time']
        
        print("\n" + "="*80)
        print("训练完成！")
        print("="*80)
        print(f"总对局数: {total_games}")
        print(f"总步数: {self.game_stats['total_moves']}")
        print(f"平均每局步数: {self.game_stats['total_moves']/total_games:.1f}")
        print(f"红方胜利: {self.game_stats['red_wins']} ({self.game_stats['red_wins']/total_games*100:.1f}%)")
        print(f"黑方胜利: {self.game_stats['black_wins']} ({self.game_stats['black_wins']/total_games*100:.1f}%)")
        print(f"总用时: {format_time(total_time)}")
        print(f"平均单局: {self.game_stats['benchmark']['avg_game_time']:.2f}秒")
        print(f"实际用时: {format_time(total_time)}")
        print(f"数据文件: {self.output_file}")
        print("="*80)

def main():
    """主函数：启动训练"""
    print("="*80)
    print("中国象棋AI后台训练程序")
    print("按 Ctrl+C 可中断并保存数据")
    print("="*80)
    
    # 创建AI实例（深度1-2平衡速度和质量）
    ai1 = ChessAI('red', search_depth=1)
    ai2 = ChessAI('black', search_depth=1)
    
    # 创建训练器
    trainer = SelfPlayTrainer(ai1, ai2)
    
    # 开始训练
    trainer.run_self_play(num_games=100, max_moves=150)
    
if __name__ == "__main__":
    main()