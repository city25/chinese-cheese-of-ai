"""10层神经网络AI"""
import numpy as np
import json
import time
from typing import Tuple, Dict, Any
from .engine import ChineseChess
import hashlib

class ChessAI:
    """10层神经网络中国象棋AI"""
    
    def __init__(self, player: str, search_depth: int = 2):
        self.player = player
        self.search_depth = search_depth
        
        # 棋子权重
        self.piece_weights = {1: 1000, 2: 20, 3: 20, 4: 40, 5: 90, 6: 45, 7: 10}
        
        # 10层神经网络参数
        self.neural_net = self._init_neural_net()
        
        # 缓存
        self._transposition_table: Dict[str, float] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # 性能统计
        self._eval_count = 0
        self._start_time = 0
        
    def _init_neural_net(self) -> Dict[str, np.ndarray]:
        """初始化10层神经网络参数"""
        # 网络结构: 90 -> 256 -> 128 -> 64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1
        net = {}
        
        # 输入层 (棋盘90个格子 + 7红方棋子特征 + 7黑方棋子特征 + 1玩家特征 = 105)
        net['w1'] = np.random.randn(105, 256) * 0.05
        net['b1'] = np.zeros(256)
        
        # 隐藏层2-9
        layers = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        for i in range(len(layers) - 1):
            net[f'w{i+2}'] = np.random.randn(layers[i], layers[i+1]) * 0.05
            net[f'b{i+2}'] = np.zeros(layers[i+1])
        
        return net
    
    def _compute_board_hash(self, board: np.ndarray) -> str:
        """计算棋盘哈希（用于缓存）"""
        return hashlib.md5(board.tobytes()).hexdigest()
    
    def _encode_board(self, board: np.ndarray) -> np.ndarray:
        """将棋盘编码为神经网络输入"""
        # 编码策略：90格子 + 7种棋子数 + 当前玩家
        encoded = []
        
        # 1. 90个格子值
        encoded.extend(board.flatten())
        
        # 2. 红方棋子数量特征
        for piece_type in range(1, 8):
            encoded.append(np.sum(board == piece_type))
        
        # 3. 黑方棋子数量特征
        for piece_type in range(1, 8):
            encoded.append(np.sum(board == -piece_type))
        
        # 4. 当前玩家特征
        encoded.append(1 if self.player == 'red' else -1)
        
        return np.array(encoded, dtype=np.float32)
    
    def _forward_pass(self, x: np.ndarray) -> float:
        """9层神经网络前向传播（修正）"""
        try:
            h = x
            # 实际只有9层权重 (w1-w9)
            for i in range(1, 10):
                h = np.tanh(h @ self.neural_net[f'w{i}'] + self.neural_net[f'b{i}'])
            
            return float(h[0])
        except Exception as e:
            print(f"神经网络前向传播错误: {e}")
            return 0.0
    
    def evaluate_board(self, chess_game: ChineseChess) -> float:
        """评估棋盘局面（10层神经网络）"""
        board_hash = self._compute_board_hash(chess_game.board)
        cache_key = f"{board_hash}_{self.player}"
        
        if cache_key in self._transposition_table:
            self._cache_hits += 1
            return self._transposition_table[cache_key]
        
        self._cache_misses += 1
        self._eval_count += 1
        
        # 获取神经网络输入
        encoded_board = self._encode_board(chess_game.board)
        
        # 获取神经网络评分
        neural_score = self._forward_pass(encoded_board)
        
        # 传统评估作为辅助
        piece_score = self._evaluate_pieces(chess_game)
        
        # 综合评分（神经网络主导）
        total_score = neural_score * 0.7 + piece_score * 0.3
        
        # 缓存结果
        self._transposition_table[cache_key] = total_score
        
        return total_score
    
    def _evaluate_pieces(self, chess_game: ChineseChess) -> float:
        """基于棋子价值的传统评估"""
        score = 0
        for i in range(10):
            for j in range(9):
                piece = chess_game.board[i, j]
                if piece != 0:
                    value = self.piece_weights.get(abs(piece), 0)
                    score += value if piece > 0 else -value
        
        # 🚨 核心修复：黑方视角反转
        if self.player == 'black':
            score = -score
        
        return score  # ✅ 修复：正确缩进
    
    def get_best_move(self, chess_game: ChineseChess) -> Tuple:
        """获取最佳走法（带性能监控）"""
        legal_moves = chess_game.get_legal_moves(self.player)
        if not legal_moves:
            return None
        
        # 打乱走法顺序（增加多样性）
        import random
        random.shuffle(legal_moves)
        
        best_score = float('-inf')
        best_move = None
        
        self._start_time = time.time()
        
        for move in legal_moves:
            new_game = ChineseChess()
            new_game.board = chess_game.board.copy()
            new_game.current_player = chess_game.current_player
            new_game.make_move(move)
            
            score = self._minimax(new_game, self.search_depth - 1, float('-inf'), float('inf'), False)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        # 清理过期的缓存项
        if len(self._transposition_table) > 100000:
            self._transposition_table.clear()
        
        return best_move
    
    def _minimax(self, chess_game: ChineseChess, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """Minimax算法实现"""
        board_hash = self._compute_board_hash(chess_game.board)
        cache_key = f"{board_hash}_{depth}_{maximizing_player}"
        
        if cache_key in self._transposition_table:
            return self._transposition_table[cache_key]
        
        if depth == 0 or chess_game.game_over:
            return self.evaluate_board(chess_game)
        
        if maximizing_player:
            max_eval = float('-inf')
            legal_moves = chess_game.get_legal_moves(self.player)
            
            for move in legal_moves:
                new_game = ChineseChess()
                new_game.board = chess_game.board.copy()
                new_game.current_player = chess_game.current_player
                new_game.make_move(move)
                
                eval_score = self._minimax(new_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta剪枝
            
            self._transposition_table[cache_key] = max_eval
            return max_eval
        else:
            min_eval = float('inf')
            opponent = 'black' if self.player == 'red' else 'red'
            legal_moves = chess_game.get_legal_moves(opponent)
            
            for move in legal_moves:
                new_game = ChineseChess()
                new_game.board = chess_game.board.copy()
                new_game.current_player = chess_game.current_player
                new_game.make_move(move)
                
                eval_score = self._minimax(new_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha剪枝
            
            self._transposition_table[cache_key] = min_eval
            return min_eval
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': self._cache_hits / max(self._cache_hits + self._cache_misses, 1),
            'eval_count': self._eval_count,
            'table_size': len(self._transposition_table)
        }
