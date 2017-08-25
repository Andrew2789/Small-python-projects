from random import randint
import pygame

def setup_data(rarities):
    """Import and process data from the database file."""
    #database format:
    #str-name | str-rarity  int-roll_number  int-hp_add  int-min_monster_count  int-max_monster_count  bool-in_south_lowlands  bool-in_south_highlands  bool-in_north_lowlands  bool-in_north_highlands  bool-in_water  bool-can_reason
    #semicolon as first char of roll_number means roll an n sided dice for set of following comma seperated values
    with open("monsters.txt","r") as f:
        #monsters = [[x[0],x[2]] + [int(y) for y in x[3:]] + [RARITIES.index(x[1])] for x in [[x[0].rstrip()] + x[1].split() for x in [x.split("|") for x in f.readlines()]]]
        monsters = []
        lines = [line.split("|") for line in f.readlines()]
        for line in [[line[0].rstrip()] + line[1].split() for line in lines]:
            monsters.append([line[0],line[2]] + [int(x) for x in line[3:]] + [rarities.index(line[1])])

    #sort data
    regions = []
    for region in range(4):
        #in_region format: one item for each rarity, each with two child lists for in_water True or False
        in_region = [[[],[]],[[],[]],[[],[]],[[],[]]]
        for monster in enumerate(monsters):
            if monster[1][5+region]:
                in_region[monster[1][-1]][monster[1][9]].append(monster[0])
        regions.append(in_region)

    return monsters, regions

def draw_background(title_font, label_font):
    """Draw the GUI background."""
    #draw background
    background = pygame.Surface((800, 650))
    background.fill((0,0,0))
    pygame.draw.rect(background,(70,70,70), (25,25,750,600))

    #region title and tiles
    title = title_font.render("Region", 1, (255,255,255))
    background.blit(title, (400 - title.get_width() / 2, 65 - title.get_height() / 2))
    
    for tile in zip(range(4), ((76,187,23), (254,238,0), (227,25,25), (0,127,255))):
        pygame.draw.rect(background, tile[1], (65 + tile[0] * 170, 100, 160, 160))
        
    region_text = [label_font.render(zone_name, 1, (0,0,0)) for zone_name in ("Southern", "Northern", "Lowlands", "Highlands")]
    for i in zip(range(4), ((0,2), (0,3), (1,2), (1,3))):
        background.blit(region_text[i[1][0]], (145 + i[0] * 170 - region_text[i[1][0]].get_width() / 2, 180 - region_text[i[1][0]].get_height()))
        background.blit(region_text[i[1][1]], (145 + i[0] * 170 - region_text[i[1][1]].get_width() / 2, 180))
        
    region_tiles = [(pygame.Surface((160, 160)), (65 + i * 170, 100)) for i in range(4)]
    for i in range(4):
        region_tiles[i][0].blit(background,(-65 - i * 170, -100))

    #'are you near water' pane
    pygame.draw.rect(background, (190,190,190), (150,280,500,80))
    water_label = label_font.render("Are you near water?", 1, (0,0,0))
    background.blit(water_label, (330 - water_label.get_width() / 2, 320 - water_label.get_height() / 2))
    yesno_labels = [(label_font.render(word[0], 1, (0,0,0)), (word[1],290,60,60)) for word in (("No", 580),("Yes", 510))]

    #'generate' button pane
    pygame.draw.rect(background, (190,190,190), (360,380,300,60))
    gen_rect = (370,390,280,40)
    pygame.draw.rect(background, (40,80,150), gen_rect)
    gen_label = label_font.render("Generate", 1, (255,255,255))
    background.blit(gen_label, (510 - gen_label.get_width() / 2, 410 - gen_label.get_height() / 2))

    #charisma pane
    pygame.draw.rect(background, (190,190,190), (65,460,670,130))
    pygame.draw.rect(background, (190,190,190), (140,380,210,60))
    pygame.draw.rect(background, (40,80,150), (145,385,200,50))
    charisma_label = label_font.render("Charisma:", 1, (255,255,255))
    background.blit(charisma_label,( 215 - charisma_label.get_width() / 2, 411 - charisma_label.get_height() / 2))
    
    return background, region_tiles, yesno_labels, gen_rect
    
def main():
    RARITIES = ("common","uncommon","rare","veryrare")
    RARITY_BRACKETS = (65, 85, 96)
    DISPOSITIONS = (("Violently hostile, immediate attack", 5),
                    ("Hostile, immediate action", 25),
                    ("Uncertain but 55% prone toward negative", 45),
                    ("Neutral - uninterested - uncertain", 55),
                    ("Uncertain but 55% prone toward positive", 75),
                    ("Friendly, immediate action", 95))
    CHARISMA_LEVELS = (-25,-25,-25,-25,-20,-15,-10,-5,0,0,0,0,0,5,10,15,25,30,35)

    monsters, regions = setup_data(RARITIES)
    
    pygame.init()
    screen = pygame.display.set_mode((800, 650))
    pygame.display.set_caption("DnD Encounter Generator")
    clock = pygame.time.Clock()
    
    title_font = pygame.font.SysFont("Calibri", 48)
    label_font = pygame.font.SysFont("Calibri", 30)
    monster_font = pygame.font.SysFont("Calibri", 24)

    background, region_tiles, yesno_labels, gen_rect = draw_background(title_font, label_font)
    
    editing_charisma = False
    charisma = 0
    selected_region = 0
    water = 0
    chosen = None
    hp = None

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        #check left click regions (buttons etc)
                        for i in range(4):
                            if region_tiles[i][1][0] < mouse_pos[0] < region_tiles[i][1][0] + 160 and region_tiles[i][1][1] < mouse_pos[1] < region_tiles[i][1][1] + 160:
                                selected_region = i
                                
                        for i in range(2):
                            if yesno_labels[i][1][0] < mouse_pos[0] < yesno_labels[i][1][0] + 60 and yesno_labels[i][1][1] < mouse_pos[1] < yesno_labels[i][1][1] + 60:
                                water = 1-i

                        if 270 < mouse_pos[0] < 350 and 380 < mouse_pos[1] < 440:
                            editing_charisma = True
                            charisma = 0
                        else:
                            editing_charisma = False
                        
                        if gen_rect[0] < mouse_pos[0] < gen_rect[0] + 280 and gen_rect[1] < mouse_pos[1] < gen_rect[1] + 40:
                            rarity_roll = randint(0, 100)
                            rarity = None
                            for i in range(3):
                                if rarity_roll <= RARITY_BRACKETS[i]:
                                    rarity = i
                                    break
                            if rarity == None:
                                rarity = 3
                            if water:
                                pool = regions[selected_region][rarity][0] + regions[selected_region][rarity][1]
                                chosen = monsters[pool[randint(0, len(pool) - 1)]]
                            else:
                                chosen = monsters[regions[selected_region][rarity][0][randint(0, len(regions[selected_region][rarity][0]) - 1)]]
                            monster_count = randint(chosen[3], chosen[4])
                            if chosen[1][0] == ";":
                                hp = [str(sum(randint(1,x) for x in [int(x) for x in chosen[1].lstrip(";").split(",")]) + chosen[2]) for y in range(monster_count)]
                            else:
                                hp = [str(sum(randint(1,8) for x in range(int(chosen[1]))) + chosen[2]) for y in range(monster_count)]
                            hp = "Hitpoints: " + ", ".join(hp)
                            
                            #choose disposition if monster is intelligent
                            if chosen[10]:
                                disposition_roll = randint(1,100) + CHARISMA_LEVELS[charisma]
                                disposition = None
                                for tier in range(len(DISPOSITIONS)):
                                    if disposition_roll <= DISPOSITIONS[tier][1]:
                                        disposition = DISPOSITIONS[tier][0]
                                        break
                                if not disposition:
                                    disposition = "Enthusiactically friendly, immediate acceptance"
                            else:
                                disposition = "Hostile"
                            
            elif event.type == pygame.KEYDOWN:
                if editing_charisma:
                    if chr(event.key) in [str(x) for x in range(10)]:
                        if charisma and len(str(charisma)) < 2:
                            charisma = int(str(charisma) + chr(event.key))
                        elif not charisma:
                            charisma = int(chr(event.key))
                            
                    elif event.key == pygame.K_RETURN:
                        editing_charisma = False
                        
                    elif event.key == pygame.K_BACKSPACE:
                        if len(str(charisma)) == 1:
                            charisma = 0
                        else:
                            charisma = int(str(charisma)[:-1])
                    if charisma > 18:
                        charisma = 18
                    
        screen.blit(background, (0,0))
        
        #draw selectors, relevant buttons/labels
        pygame.draw.rect(screen, (255,255,255), (60 + selected_region * 170, 95, 170, 170))
        screen.blit(*region_tiles[selected_region])
        pygame.draw.rect(screen, (255,255,255), (507 + water * 70, 287, 66, 66))
        for i in ((0, (25,255,25)), (1, (255,25,25))):
            pygame.draw.rect(screen, i[1], yesno_labels[i[0]][1])
        for i in (0,1):
            screen.blit(yesno_labels[i][0], (540 + i * 70 - yesno_labels[i][0].get_width() / 2, 320 - yesno_labels[i][0].get_height() / 2))
        if editing_charisma:
            pygame.draw.rect(screen, (0,127,255), (280,385,65,50))
            
        charisma_value = title_font.render(str(charisma), 1, (255,255,255))
        screen.blit(charisma_value, (313 - charisma_value.get_width() / 2, 415 - charisma_value.get_height() / 2))

        #draw monster info
        if chosen:
            monster_label = label_font.render("%d x %s" % (monster_count, chosen[0]), 1, (0,0,0))
            screen.blit(monster_label, (400 - monster_label.get_width() / 2, 470))
            disposition_label = monster_font.render("Disposition: %s" % disposition, 1, (0,0,0))
            screen.blit(disposition_label, (400 - disposition_label.get_width() / 2, 520 - disposition_label.get_height() / 2))
            split_at = len(hp) // 2
            if "," in hp:
                while hp[split_at] != " ":
                    split_at += 1
            hp_label = [monster_font.render(half, 1, (0,0,0)) for half in (hp[:split_at], hp[split_at:])]
            if sum(half.get_width() for half in hp_label) < 670:
                for i in (0,1):
                    screen.blit(hp_label[i], (400 - sum(half.get_width() for half in hp_label) / 2 + hp_label[0].get_width() * i, 555 - hp_label[0].get_height() / 2))
            else:
                for i in (0,1):
                    screen.blit(hp_label[i], (400 - hp_label[i].get_width() / 2, 555 - hp_label[0].get_height() * (1 - i)))
                    
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

main()
