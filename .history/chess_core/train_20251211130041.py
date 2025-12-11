#!/usr/bin/env python3
# train.py - 后台训练程序（无界面）
import numpy as np
import json
import time
from datetime import datetime
from chess_core import ChineseChess, ChessAI

class SelfPlayTrainer:
    """自我对弈训练系统"""
    
    def __init__(self, ai1: ChessAI, ai2: ChessAI, output_file: str = None):
        self.ai1 = ai1
        self.ai2 = ai2
        self.output_file = output_file or f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.training_data = []
        self.game_stats = {
            'total_games': 0,
            'red_wins': 0,
            'black_wins': 0,
            'total_moves': 0,
            'total_time': 0,
            'start_time': time.time()
        }
        
    def run_self_play(self, num_games: int = 100, max_moves: int = 200):
        """运行自我对弈"""
        print("="*70)
        print("中国象棋AI自我对弈训练系统")
        print("="*70)
        print(f"目标对局数: {num_games}")
        print(f"每局最大步数: {max_moves}")
        print(f"红方搜索深度: {self.ai1.search_depth}")
        print(f"黑方搜索深度: {self.ai2.search_depth}")
        print(f"输出文件: {self.output_file}")
        print("="*70)
        
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
                
                # 每局间隔10ms，避免CPU占用过高
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n训练被中断，正在保存数据...")
        
        finally:
            self.game_stats['total_time'] = time.time() - self.game_stats['start_time']
            self._save_data()
            self._print_final_stats()
        
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
            
            # 检查游戏是否结束
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
        
        # 保存统计信息
        with open("training_stats.json", 'w', encoding='utf-8') as f:
            json.dump(self.game_stats, f, ensure_ascii=False, indent=2)
        
        # 保存为CSV格式（便于机器学习）
        csv_data = []
        for record in self.training_data:
            csv_data.append({
                'game_id': record['game_id'],
                'move_number': record['move_number'],
                'player': record['player'],
                'board_state': json.dumps(record['board_state']),
                'move': json.dumps(record['move']),
                'result': record['result']
            })
        
        import pandas as pd
        df = pd.DataFrame(csv_data)
        df.to_csv(self.output_file.replace('.json', '.csv'), index=False, encoding='utf-8')
    
    def _print_progress(self, current: int, total: int, last_game_time: float):
        """打印进度"""
        print(f"\n{'='*70}")
        print(f"进度: {current}/{total} ({current/total*100:.1f}%)")
        print(f"最近一局: {last_game_time:.2f}秒 | 总时长: {time.time()-self.game_stats['start_time']:.0f}秒")
        print(f"红方胜率: {self.game_stats['red_wins']/current*100:.1f}% "
              f"({self.game_stats['red_wins']}/{current})")
        print(f"黑方胜率: {self.game_stats['black_wins']/current*100:.1f}% "
              f"({self.game_stats['black_wins']}/{current})")
        print(f"和棋率: {(current-self.game_stats['red_wins']-self.game_stats['black_wins'])/current*100:.1f}%")
        print(f"数据点数: {len(self.training_data)}")
        print(f"{'='*70}\n")
    
    def _print_final_stats(self):
        """打印最终统计"""
        total_games = self.game_stats['total_games']
        total_time = self.game_stats['total_time']
        
        print("\n" + "="*70)
        print("训练完成！")
        print("="*70)
        print(f"总对局数: {total_games}")
        print(f"总步数: {self.game_stats['total_moves']}")
        print(f"平均每局步数: {self.game_stats['total_moves']/total_games:.1f}")
        print(f"红方胜利: {self.game_stats['red_wins']} ({self.game_stats['red_wins']/total_games*100:.1f}%)")
        print(f"黑方胜利: {self.game_stats['black_wins']} ({self.game_stats['black_wins']/total_games*100:.1f}%)")
        print(f"和棋: {total_games - self.game_stats['red_wins'] - self.game_stats['black_wins']} "
              f"({(total_games - self.game_stats['red_wins'] - self.game_stats['black_wins'])/total_games*100:.1f}%)")
        print(f"总用时: {total_time:.2f}秒")
        print(f"平均每局: {total_time/total_games:.2f}秒")
        print(f"数据已保存至: {self.output_file}")
        print("="*70)

def main():
    """主函数：启动训练"""
    print("="*70)
    print("中国象棋AI后台训练程序")
    print("按 Ctrl+C 可中断并保存数据")
    print("="*70)
    
    # 创建AI实例（可调节搜索深度）
    ai1 = ChessAI('red', search_depth=2)   # 搜索深度2，平衡速度和质量
    ai2 = ChessAI('black', search_depth=2)
    
    # 创建训练器
    trainer = SelfPlayTrainer(ai1, ai2)
    
    # 开始训练
    trainer.run_self_play(num_games=100, max_moves=150)
    
if __name__ == "__main__":
    main()
