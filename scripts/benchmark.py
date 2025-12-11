#!/usr/bin/env python3
"""性能测试脚本"""
import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chess_core import ChineseChess, ChessAI

def benchmark():
    """测试自博弈性能"""
    print("="*80)
    print("中国象棋AI性能基准测试")
    print("="*80)
    
    # 创建AI
    ai = ChessAI('red', search_depth=2)
    
    # 测试单步性能
    print("\n1. 单步计算性能测试...")
    game = ChineseChess()
    move_times = []
    
    for _ in range(20):  # 测试20步
        start = time.time()
        move = ai.get_best_move(game)
        move_time = time.time() - start
        move_times.append(move_time)
        
        if move:
            game.make_move(move)
            print(f"第{len(move_times)}步: {move_time*1000:.1f}ms")
    
    avg_move_time = sum(move_times) / len(move_times)
    print(f"\n平均单步时间: {avg_move_time*1000:.1f}ms")
    print(f"总测试步数: {len(move_times)}")
    
    # 测试完整对局
    print("\n2. 完整对局性能测试...")
    game_times = []
    
    for game_id in range(1, 4):  # 测试3局
        start = time.time()
        game = ChineseChess()
        
        move_count = 0
        while not game.game_over and move_count < 100:
            current_ai = ai if game.current_player == 'red' else ChessAI('black', search_depth=2)
            move = current_ai.get_best_move(game)
            
            if move:
                game.make_move(move)
                move_count += 1
            else:
                break
        
        game_time = time.time() - start
        game_times.append(game_time)
        print(f"第{game_id}局: {game_time:.2f}秒 ({move_count}步)")
    
    avg_game_time = sum(game_times) / len(game_times)
    print(f"\n平均单局时间: {avg_game_time:.2f}秒")
    
    # 生成报告
    report = {
        "avg_move_time_ms": avg_move_time * 1000,
        "avg_game_time_seconds": avg_game_time,
        "total_games_tested": len(game_times),
        "total_moves_tested": len(move_times),
        "ai_depth": ai.search_depth
    }
    
    # 保存报告
    os.makedirs('data', exist_ok=True)
    with open('data/benchmark_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print("基准测试完成！")
    print(f"预计100局训练时间: {(avg_game_time * 100) / 60:.1f}分钟")
    print("报告已保存至: data/benchmark_report.json")
    print("="*80)

if __name__ == "__main__":
    benchmark()