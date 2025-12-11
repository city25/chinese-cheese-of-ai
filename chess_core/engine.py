"""中国象棋规则引擎"""
import numpy as np
from typing import List, Tuple, Dict, Any

class ChineseChess:
    """中国象棋规则引擎"""
    
    def __init__(self):
        self.board = self._init_board()
        self.current_player = 'red'  # 红方先行
        self.game_over = False
        self.winner = None
        self.move_history = []
        self._board_hash = None
        
    def _init_board(self):
        """初始化棋盘"""
        board = np.zeros((10, 9), dtype=np.int8)  # 使用int8节省内存
        
        # 红方布局
        board[9, 0] = board[9, 8] = 5   # 车
        board[9, 1] = board[9, 7] = 4   # 马
        board[9, 2] = board[9, 6] = 3   # 相
        board[9, 3] = board[9, 5] = 2   # 士
        board[9, 4] = 1                   # 将
        board[7, 1] = board[7, 7] = 6    # 炮
        board[6, 0] = board[6, 2] = board[6, 4] = board[6, 6] = board[6, 8] = 7  # 兵
        
        # 黑方布局 (用负数表示)
        board[0, 0] = board[0, 8] = -5   # 车
        board[0, 1] = board[0, 7] = -4  # 马
        board[0, 2] = board[0, 6] = -3   # 相
        board[0, 3] = board[0, 5] = -2   # 士
        board[0, 4] = -1                  # 将
        board[2, 1] = board[2, 7] = -6    # 炮
        board[3, 0] = board[3, 2] = board[3, 4] = board[3, 6] = board[3, 8] = -7  # 兵
        
        return board
    
    def reset(self):
        """重置棋盘"""
        self.board = self._init_board()
        self.current_player = 'red'
        self.game_over = False
        self.winner = None
        self.move_history = []
    
    def get_board_state(self) -> np.ndarray:
        """获取当前棋盘状态"""
        return self.board.copy()
    
    def get_legal_moves(self, player: str) -> List[Tuple]:
        """获取当前玩家的所有合法走法"""
        moves = []
        sign = 1 if player == 'red' else -1
        
        for i in range(10):
            for j in range(9):
                piece = self.board[i, j]
                if piece * sign > 0:
                    moves.extend(self._get_piece_moves(i, j, abs(piece), sign))
        return moves
    
    def _get_piece_moves(self, x: int, y: int, piece_type: int, sign: int) -> List[Tuple]:
        """获取特定棋子的所有合法走法"""
        if piece_type == 1:  # 将/帅
            return self._general_moves(x, y, sign)
        elif piece_type == 2:  # 士/仕
            return self._advisor_moves(x, y, sign)
        elif piece_type == 3:  # 相/象
            return self._elephant_moves(x, y, sign)
        elif piece_type == 4:  # 马
            return self._horse_moves(x, y, sign)
        elif piece_type == 5:  # 车
            return self._chariot_moves(x, y, sign)
        elif piece_type == 6:  # 炮
            return self._cannon_moves(x, y, sign)
        elif piece_type == 7:  # 兵/卒
            return self._soldier_moves(x, y, sign)
        return []
    
    def _general_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """将/帅的走法"""
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self._is_in_palace(nx, ny, sign) and self.board[nx, ny] * sign <= 0:
                moves.append((x, y, nx, ny))
        return moves
    
    def _advisor_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """士/仕的走法"""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self._is_in_palace(nx, ny, sign) and self.board[nx, ny] * sign <= 0:
                moves.append((x, y, nx, ny))
        return moves
    
    def _elephant_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """相/象的走法"""
        moves = []
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 10 and 0 <= ny < 9):
                continue
            if self._is_in_territory(nx, sign):
                block_x, block_y = x + dx // 2, y + dy // 2
                if (0 <= block_x < 10 and 0 <= block_y < 9 and 
                    self.board[block_x, block_y] == 0 and 
                    self.board[nx, ny] * sign <= 0):
                    moves.append((x, y, nx, ny))
        return moves
    
    def _horse_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """马的走法"""
        moves = []
        directions = [(1, 2), (2, 1), (1, -2), (2, -1), 
                     (-1, 2), (-2, 1), (-1, -2), (-2, -1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 10 and 0 <= ny < 9):
                continue
            block_x, block_y = x + dx // 2, y + dy // 2
            if (0 <= block_x < 10 and 0 <= block_y < 9 and 
                self.board[block_x, block_y] == 0 and 
                self.board[nx, ny] * sign <= 0):
                moves.append((x, y, nx, ny))
        return moves
    
    def _chariot_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """车的走法"""
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            for step in range(1, 10):
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 10 and 0 <= ny < 9):
                    break
                target = self.board[nx, ny]
                if target == 0:
                    moves.append((x, y, nx, ny))
                elif target * sign < 0:
                    moves.append((x, y, nx, ny))
                    break
                else:
                    break
        return moves
    
    def _cannon_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """炮的走法"""
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            has_jumped = False
            for step in range(1, 10):
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 10 and 0 <= ny < 9):
                    break
                target = self.board[nx, ny]
                if not has_jumped:
                    if target == 0:
                        moves.append((x, y, nx, ny))
                    else:
                        has_jumped = True
                else:
                    if target != 0:
                        if target * sign < 0:
                            moves.append((x, y, nx, ny))
                        break
        return moves
    
    def _soldier_moves(self, x: int, y: int, sign: int) -> List[Tuple]:
        """兵/卒的走法"""
        moves = []
        if sign == 1:  # 红兵
            directions = [(-1, 0)]
            if x <= 4:
                directions.extend([(0, 1), (0, -1)])
        else:  # 黑卒
            directions = [(1, 0)]
            if x >= 5:
                directions.extend([(0, 1), (0, -1)])
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 10 and 0 <= ny < 9):
                continue
            if self.board[nx, ny] * sign <= 0:
                moves.append((x, y, nx, ny))
        return moves
    
    def _is_in_palace(self, x: int, y: int, sign: int) -> bool:
        """判断位置是否在九宫内"""
        return (7 <= x <= 9 if sign == 1 else 0 <= x <= 2) and 3 <= y <= 5
    
    def _is_in_territory(self, x: int, sign: int) -> bool:
        """判断位置是否在己方领土内"""
        return 5 <= x <= 9 if sign == 1 else 0 <= x <= 4
    
    def make_move(self, move: Tuple) -> bool:
        """执行走法"""
        if self.game_over:
            return False
            
        x1, y1, x2, y2 = move
        if move not in self.get_legal_moves(self.current_player):
            return False
        
        # 执行移动
        captured_piece = self.board[x2, y2]
        self.board[x2, y2] = self.board[x1, y1]
        self.board[x1, y1] = 0
        
        # 记录走法
        self.move_history.append({
            'player': self.current_player,
            'move': move,
            'captured': captured_piece
        })
        
        # 切换玩家
        self.current_player = 'black' if self.current_player == 'red' else 'red'
        
        # 检查游戏是否结束
        self._check_game_over()
        
        return True
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        red_has_general = np.any(self.board == 1)
        black_has_general = np.any(self.board == -1)
        
        if not red_has_general:
            self.game_over = True
            self.winner = 'black'
        elif not black_has_general:
            self.game_over = True
            self.winner = 'red'