import chess 
import chess.engine
import pygame
import pygame_menu
from os import path
from os import listdir



def GetPath(file):
    return path.abspath(path.join(path.dirname(__file__), file))

def GetEnginePath():
    e = GetPath("engine")
    return path.join(e, listdir(e)[0])

class GameOptions:
    against_engine = True
    engine_skill_level = 0 #from 0 to 20 
    engine_color = chess.BLACK
    flip_board = True

options = GameOptions()
#main
pygame.init()

engine = chess.engine.SimpleEngine.popen_uci(GetEnginePath())

window_size = 800
square_size = window_size // 8 

window = pygame.display.set_mode((window_size, window_size), vsync=1)
pygame.display.set_caption("Chess Game (Press ESC to return to menu, U to Undo)")

piece_scale = (square_size / 256) * 0.8
def LoadSprite(filename):
    sprite = pygame.image.load(filename)
    return pygame.transform.smoothscale_by(sprite, piece_scale) 

sprites = {}
sprites[(chess.WHITE, chess.KNIGHT)] = LoadSprite(GetPath("sprite/w_knight.png"))
sprites[(chess.WHITE, chess.ROOK)]   = LoadSprite(GetPath("sprite/w_rook.png"))
sprites[(chess.WHITE, chess.BISHOP)] = LoadSprite(GetPath("sprite/w_bishop.png"))
sprites[(chess.WHITE, chess.KING)]   = LoadSprite(GetPath("sprite/w_king.png"))
sprites[(chess.WHITE, chess.PAWN)]   = LoadSprite(GetPath("sprite/w_pawn.png"))
sprites[(chess.WHITE, chess.QUEEN)]  = LoadSprite(GetPath("sprite/w_queen.png"))

sprites[(chess.BLACK, chess.KNIGHT)] = LoadSprite(GetPath("sprite/b_knight.png"))
sprites[(chess.BLACK, chess.ROOK)]   = LoadSprite(GetPath("sprite/b_rook.png"))
sprites[(chess.BLACK, chess.BISHOP)] = LoadSprite(GetPath("sprite/b_bishop.png"))
sprites[(chess.BLACK, chess.KING)]   = LoadSprite(GetPath("sprite/b_king.png"))
sprites[(chess.BLACK, chess.PAWN)]   = LoadSprite(GetPath("sprite/b_pawn.png"))
sprites[(chess.BLACK, chess.QUEEN)]  = LoadSprite(GetPath("sprite/b_queen.png"))


font_size = 100
font = pygame.font.SysFont(None, font_size)

board = chess.Board()

brown_dark = (81, 42, 42)
brown_light = (124, 76, 62)
gray_dark = (54, 54, 54)
gray_light = (89, 89, 89)
yellow = (255, 255, 0)



grabbed = -1
legal_squares = []

last_move = None


menu = pygame_menu.Menu(
        height=window_size * 0.6,
        width=window_size * 0.7,
        theme=pygame_menu.themes.THEME_DARK.copy(),
        title='Chess Game',
    )




def SetDifficulty(value, difficulty):
    options.engine_skill_level = difficulty


should_close = False
def ExitGame():
    global should_close
    should_close = True
    menu.disable()

def PlayComputer(my_color):
    global board
    board = chess.Board()
    options.against_engine = True
    engine.configure({"Skill Level": options.engine_skill_level})
    options.engine_color = not my_color
    options.flip_board = True if my_color == chess.WHITE else False
    menu.disable()

def PlayComputerWhite():
    PlayComputer(chess.WHITE)
    
def PlayComputerBlack():
    PlayComputer(chess.BLACK)
    


def PassAndPlay():
    global board
    board = chess.Board()
    options.against_engine = False
    options.flip_board = True
    menu.disable()



# main_menu.add.range_slider
menu.add.button('Play Against Computer (as white)', PlayComputerWhite)
menu.add.button('Play Against Computer (as black)', PlayComputerBlack)
menu.add.selector('Computer Difficulty', [('Normal', 0), ('Hard', 5), ('Very Hard', 10), ('Magnus Calsen', 15), ('Unbeatable', 20)], onchange=SetDifficulty)
menu.add.button('Pass & Play', PassAndPlay)
menu.add.button('Quit Game', ExitGame)

menu.enable()
menu.enable_render()

def GetCoordFromSquare(i):
    c = i % 8
    r = i // 8

    if options.flip_board:
        r = 7 - r
    else:
        c = 7 - c
    return (c, r)

def GetHoveredSquare():
    pos = pygame.mouse.get_pos()
    c = pos[0] // square_size
    r = pos[1] // square_size
    if r >= 0 and r <= 8 and c >= 0 and c <= 8:
        if options.flip_board:
            r = 7 - r
        else:
            c = 7 - c
        return r * 8 + c
    else:
        return None 


def GetSpriteFromSquare(s):
    color = board.color_at(s)
    piece_type = board.piece_type_at(s)
    sprite = sprites[(color, piece_type)]
    return sprite


def DrawBoard(grabbed_peice_square = -1):
    for sq in range(8 * 8):
        column, row = GetCoordFromSquare(sq)

        board_colors_gray = (gray_light, gray_dark)
        board_colors_brown = (brown_light, brown_dark)

        square_colors = board_colors_brown
        if last_move and (sq in [last_move.from_square, last_move.to_square]):
            square_colors = board_colors_gray

        sq_color = square_colors[0 if (row % 2 == column % 2) else 1] 
        pygame.draw.rect(window, sq_color, pygame.Rect(column * square_size, row * square_size, square_size, square_size))

        if board.piece_type_at(sq) != None and not grabbed_peice_square == sq:
            sprite = GetSpriteFromSquare(sq)
            x_offset = (square_size - sprite.get_rect().width) // 2
            y_offset = (square_size - sprite.get_rect().height) // 2 
            window.blit(sprite, ((x_offset + column * square_size, y_offset + row * square_size), sprite.get_rect().size))




while not should_close:  


    if menu.is_enabled():
        menu.mainloop(window, DrawBoard, disable_loop=False, fps_limit=0, wait_for_event=True)
    

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT: 
                should_close = True
            case pygame.MOUSEBUTTONDOWN:
                if grabbed != -1:
                    continue
                square = GetHoveredSquare()
                if board.piece_at(square) != None:
                    grabbed = square
                    legal_squares = [m.to_square for m in board.legal_moves if m.from_square == grabbed]
                
            case pygame.MOUSEBUTTONUP:
                if grabbed == -1:
                    continue
                final_square = GetHoveredSquare()
                if final_square: 
                    row = final_square // 8
                    if board.piece_type_at(grabbed) == chess.PAWN and row in [0, 7]:
                        # automatic queen promotion
                        move = chess.Move(grabbed, final_square, chess.QUEEN)
                    else:
                        move = chess.Move(grabbed, final_square)

                    if move in board.legal_moves:
                        board.push(move)
                        last_move = move
            

                grabbed = -1
                legal_squares.clear()
                
            
            case pygame.KEYUP:
                match event.key: 
                    case pygame.K_u:
                        try:
                            color_to_play = chess.WHITE if len(board.move_stack) % 2 == 0 else chess.BLACK 
                            if options.against_engine and color_to_play != options.engine_color:
                                board.pop()
                                board.pop()
                            else:
                                board.pop()

                        except IndexError:
                            pass

                        try:
                            last_move = board.peek()
                        except IndexError:
                            last_move = None
                    case pygame.K_ESCAPE:
                        last_move = None
                        menu.enable()
                
        
    window.fill((255, 255, 255))

    DrawBoard(grabbed)

    for sq in legal_squares:
        half = square_size // 2
        column, row = GetCoordFromSquare(sq)
        pygame.draw.circle(window, yellow, (column * square_size + half, row * square_size + half), square_size * 0.1)


    if grabbed != -1:
        sprite = GetSpriteFromSquare(grabbed)
        pos = pygame.mouse.get_pos()
        rect = sprite.get_rect()
        window.blit(sprite, ((pos[0] - rect.w // 2, pos[1] - rect.h // 2), rect.size))
        


    if board.is_game_over():
        outcome = board.outcome()
        winner_text = ""
        match outcome.winner:
            case chess.WHITE:
                winner_text = "White wins"
            case chess.BLACK:
                winner_text = "Black wins"
            case None:
                winner_text = "Draw"

        reason_text = ""
        match outcome.termination:
            case chess.Termination.CHECKMATE:
                reason_text = "by checkmate"
            case chess.Termination.STALEMATE:
                reason_text = "by stalemate"
            case chess.Termination.INSUFFICIENT_MATERIAL:
                reason_text = "by insufficient material"
            case chess.Termination.FIFTY_MOVES | chess.Termination.SEVENTYFIVE_MOVES:
                reason_text = "by move limit"
            case chess.Termination.FIVEFOLD_REPETITION | chess.Termination.THREEFOLD_REPETITION:
                reason_text = "by repetition"


        def DrawTextCenter(text, y):
            img = font.render(text, True, (255, 252, 132))
            shadow = font.render(text, True, (0, 0, 0))
            size = img.get_rect().size
            text_pos = (window_size // 2 - size[0] // 2, y)
            window.blit(shadow, (text_pos[0] + 7, text_pos[1] + 7))
            window.blit(img, text_pos)


        y = window_size / 2 - font_size
        DrawTextCenter(winner_text, y)
        y += font_size
        DrawTextCenter(reason_text, y)



    pygame.display.flip()

    color_to_play = chess.WHITE if len(board.move_stack) % 2 == 0 else chess.BLACK 

    if options.against_engine and color_to_play == options.engine_color:
        result = engine.play(board, chess.engine.Limit(time=0.5))
        if result.move:
            board.push(result.move)
            last_move = result.move

    
            

pygame.display.quit()
pygame.quit()
engine.quit()
