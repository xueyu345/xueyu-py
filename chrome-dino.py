#Pygame needs to be installed

import pygame
import random
import sys
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)

class Dino:
    def __init__(self):
        self.x = 100
        self.y = GROUND_HEIGHT - 50
        self.width = 40
        self.height = 50
        self.vel_y = 0
        self.jumping = False
        self.ducking = False
        self.duck_height = 30
        self.normal_height = 50
        self.animation_counter = 0
        self.frame = 0
        self.color = DARK_GRAY
        
    def jump(self):
        if not self.jumping and not self.ducking:
            self.jumping = True
            self.vel_y = -15
            
    def duck(self):
        if not self.jumping:
            self.ducking = True
            self.height = self.duck_height
            self.y = GROUND_HEIGHT - self.duck_height
            
    def stand(self):
        self.ducking = False
        self.height = self.normal_height
        self.y = GROUND_HEIGHT - self.normal_height
        
    def update(self):
        if self.jumping:
            self.y += self.vel_y
            self.vel_y += 1  # 重力
            
            # 落地检测
            if self.y >= GROUND_HEIGHT - self.normal_height:
                self.y = GROUND_HEIGHT - self.normal_height
                self.jumping = False
                self.vel_y = 0
                
        # 动画更新
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.frame = (self.frame + 1) % 2
            self.animation_counter = 0
            
    def draw(self, screen):
        # 根据状态绘制不同形状的恐龙
        if self.ducking:
            # 蹲下时绘制长方形
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, self.width, self.height))
            # 添加眼睛
            pygame.draw.circle(screen, WHITE, 
                             (self.x + 25, self.y + 10), 3)
        elif self.jumping:
            # 跳跃时绘制稍微不同的形状
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, self.width, self.height))
            # 添加眼睛和嘴
            pygame.draw.circle(screen, WHITE, 
                             (self.x + 30, self.y + 15), 3)
        else:
            # 跑步动画
            if self.frame == 0:
                pygame.draw.rect(screen, self.color, 
                               (self.x, self.y, self.width, self.height))
                # 后腿
                pygame.draw.line(screen, self.color, 
                               (self.x + 35, self.y + 45), 
                               (self.x + 45, self.y + 50), 4)
            else:
                pygame.draw.rect(screen, self.color, 
                               (self.x, self.y, self.width, self.height))
                # 前腿
                pygame.draw.line(screen, self.color, 
                               (self.x + 35, self.y + 45), 
                               (self.x + 45, self.y + 40), 4)
            
            # 眼睛
            pygame.draw.circle(screen, WHITE, 
                             (self.x + 30, self.y + 15), 3)

class Obstacle:
    def __init__(self, obs_type):
        self.type = obs_type  # 'cactus' or 'bird'
        self.x = SCREEN_WIDTH
        self.width = 20 if obs_type == 'cactus' else 30
        self.height = 40 if obs_type == 'cactus' else 20
        self.y = GROUND_HEIGHT - self.height if obs_type == 'cactus' else GROUND_HEIGHT - 70
        self.speed = 8
        self.color = GRAY if obs_type == 'cactus' else DARK_GRAY
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        if self.type == 'cactus':
            # 绘制仙人掌
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, self.width, self.height))
            # 添加分支
            pygame.draw.rect(screen, self.color, 
                           (self.x - 5, self.y + 10, 10, 10))
            pygame.draw.rect(screen, self.color, 
                           (self.x + 15, self.y + 20, 10, 10))
        else:
            # 绘制鸟
            pygame.draw.ellipse(screen, self.color, 
                              (self.x, self.y, self.width, self.height))
            # 翅膀
            if random.randint(0, 1):
                pygame.draw.arc(screen, self.color, 
                              (self.x - 10, self.y, 20, 20), 0, 3.14, 2)
                
    def off_screen(self):
        return self.x + self.width < 0

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, 200)
        self.width = random.randint(40, 80)
        self.height = random.randint(20, 30)
        self.speed = 2
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        # 绘制云朵
        pygame.draw.ellipse(screen, GRAY, 
                          (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, GRAY, 
                          (self.x + 15, self.y - 10, 30, 20))
        pygame.draw.ellipse(screen, GRAY, 
                          (self.x - 10, self.y + 5, 25, 15))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chrome Dino Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.dino = Dino()
        self.obstacles = []
        self.clouds = []
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.game_speed = 8
        self.obstacle_timer = 0
        self.cloud_timer = 0
        self.ground_x = 0
        
    def load_high_score(self):
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read())
        except:
            return 0
            
    def save_high_score(self):
        if self.score > self.high_score:
            with open('high_score.txt', 'w') as f:
                f.write(str(self.score))
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
                
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.dino.jump()
                        
                elif event.key == K_DOWN:
                    if not self.game_over:
                        self.dino.duck()
                        
                elif event.key == K_ESCAPE:
                    return False
                    
            elif event.type == KEYUP:
                if event.key == K_DOWN:
                    self.dino.stand()
                    
        return True
        
    def update(self):
        if self.game_over:
            return
            
        # 更新恐龙
        self.dino.update()
        
        # 生成云朵
        self.cloud_timer += 1
        if self.cloud_timer > 100:
            self.clouds.append(Cloud())
            self.cloud_timer = 0
            
        # 更新云朵
        for cloud in self.clouds[:]:
            cloud.update()
            if cloud.off_screen():
                self.clouds.remove(cloud)
                
        # 生成障碍物
        self.obstacle_timer += 1
        if self.obstacle_timer > random.randint(60, 120):
            obs_type = 'cactus' if random.random() < 0.7 else 'bird'
            self.obstacles.append(Obstacle(obs_type))
            self.obstacle_timer = 0
            
        # 更新障碍物
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.off_screen():
                self.obstacles.remove(obstacle)
                self.score += 10
                
        # 碰撞检测
        dino_rect = pygame.Rect(self.dino.x, self.dino.y, 
                               self.dino.width, self.dino.height)
        
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(obstacle.x, obstacle.y, 
                                  obstacle.width, obstacle.height)
            if dino_rect.colliderect(obs_rect):
                self.game_over = True
                self.save_high_score()
                
        # 更新地面动画
        self.ground_x -= self.game_speed
        if self.ground_x <= -20:
            self.ground_x = 0
            
        # 难度增加
        if self.score > 0 and self.score % 500 == 0:
            self.game_speed = min(15, self.game_speed + 0.5)
            
    def draw(self):
        # 清屏
        self.screen.fill(WHITE)
        
        # 绘制天空
        pygame.draw.rect(self.screen, WHITE, 
                        (0, 0, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # 绘制云朵
        for cloud in self.clouds:
            cloud.draw(self.screen)
            
        # 绘制地面
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(self.screen, BLACK, 
                           (i + self.ground_x, GROUND_HEIGHT), 
                           (i + self.ground_x + 10, GROUND_HEIGHT), 2)
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # 绘制恐龙
        self.dino.draw(self.screen)
        
        # 绘制分数
        score_text = self.font.render(f'分数: {self.score}', True, BLACK)
        self.screen.blit(score_text, (650, 20))
        
        high_score_text = self.small_font.render(f'最高分: {self.high_score}', 
                                                True, GRAY)
        self.screen.blit(high_score_text, (650, 60))
        
        # 游戏结束提示
        if self.game_over:
            game_over_text = self.font.render('游戏结束', True, RED)
            restart_text = self.small_font.render('按空格键重新开始', True, BLACK)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, 150))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, 200))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
            
        # 开始提示
        if self.score == 0 and not self.game_over:
            tip_text = self.small_font.render('按空格键跳跃，按方向键下蹲', True, GRAY)
            tip_rect = tip_text.get_rect(center=(SCREEN_WIDTH/2, 200))
            self.screen.blit(tip_text, tip_rect)
            
        # 更新显示
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# 启动游戏
if __name__ == "__main__":
    game = Game()
    game.run()
