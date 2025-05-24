import random
from network import client
from protocol import Protocol
SuitName = ['C', 'D', 'H', 'S']
SuitNum = {
    'C': 0, 'D': 1, 'H': 2, 'S': 3
}
RankName = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
RankNum = {
    '2': 0, '3': 1, '4': 2, '5': 3, '6': 4,
    '7': 5, '8': 6, '9': 7, 'T': 8,
    'J': 9, 'Q': 10, 'K': 11, 'A': 12
}
VulName = ['N', 'NS', 'EW', 'B']
VulNum = {
    'N': 0, 'NS': 1, 'EW': 2, 'B': 3
}
CardName = [
    'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'CT', 'CJ', 'CQ', 'CK', 'CA',
    'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'DT', 'DJ', 'DQ', 'DK', 'DA',
    'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'HT', 'HJ', 'HQ', 'HK', 'HA',
    'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'ST', 'SJ', 'SQ', 'SK', 'SA'
]
CardNum = {
    'C2': 0, 'C3': 1, 'C4': 2, 'C5': 3, 'C6': 4, 'C7': 5, 'C8': 6, 'C9': 7, 'CT': 8, 'CJ': 9, 'CQ': 10, 'CK': 11, 'CA': 12,
    'D2': 13, 'D3': 14, 'D4': 15, 'D5': 16, 'D6': 17, 'D7': 18, 'D8': 19, 'D9': 20, 'DT': 21, 'DJ': 22, 'DQ': 23, 'DK': 24, 'DA': 25,
    'H2': 26, 'H3': 27, 'H4': 28, 'H5': 29, 'H6': 30, 'H7': 31, 'H8': 32, 'H9': 33, 'HT': 34, 'HJ': 35, 'HQ': 36, 'HK': 37, 'HA': 38,
    'S2': 39, 'S3': 40, 'S4': 41, 'S5': 42, 'S6': 43, 'S7': 44, 'S8': 45, 'S9': 46, 'ST': 47, 'SJ': 48, 'SQ': 49, 'SK': 50, 'SA': 51
}
BidName = [
    '1C', '1D', '1H', '1S', '1N',
    '2C', '2D', '2H', '2S', '2N',
    '3C', '3D', '3H', '3S', '3N',
    '4C', '4D', '4H', '4S', '4N',
    '5C', '5D', '5H', '5S', '5N',
    '6C', '6D', '6H', '6S', '6N',
    '7C', '7D', '7H', '7S', '7N',
    'P', 'X', 'XX'
]
BidNum = {
    '1C': 0, '1D': 1, '1H': 2, '1S': 3, '1N': 4,
    '2C': 5, '2D': 6, '2H': 7, '2S': 8, '2N': 9,
    '3C': 10, '3D': 11, '3H': 12, '3S': 13, '3N': 14,
    '4C': 15, '4D': 16, '4H': 17, '4S': 18, '4N': 19,
    '5C': 20, '5D': 21, '5H': 22, '5S': 23, '5N': 24,
    '6C': 25, '6D': 26, '6H': 27, '6S': 28, '6N': 29,
    '7C': 30, '7D': 31, '7H': 32, '7S': 33, '7N': 34,
    'P': 35, 'X': 36, 'XX': 37
}
LevelName = ['1', '2', '3', '4', '5', '6', '7']
LevelNum = {
    '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6
}
TrumpsName = ['C', 'D', 'H', 'S', 'N']
TrumpsNum = {
    'C': 0, 'D': 1, 'H': 2, 'S': 3, 'N': 4
}
PostionName = ['N', 'E', 'S', 'W']
PostionNum = {
    'N': 0, 'E': 1, 'S': 2, 'W': 3
}
DoubleName = ['', 'X', 'XX']
DoubleNum = {
    '': 0, 'X': 1, 'XX': 2
}

import os
import platform

class Bridge(client.p2pInterface):
    encryption: bool#啟用的話洗牌和出牌會進行加密
    schuffleCheat: bool#啟用的話玩家可以在洗牌嘗試作弊
    playCheat: bool#啟用的化玩家可以在出牌嘗試作弊

    boradId: int#牌號
    dealer: int#開叫人
    vul: int#身價 0:none, 1:ns, 2:ew, 3:both
    cards: list[int]#手上的13張牌
    level: int#叫牌線位
    trump: int#王牌
    declarerPos: int#主打方位
    double: int#合約是否賭倍:0:none, 1:x, 2:xx
    dealName: str#合約名稱: 1CW or 2NW or 7NEXX or AP ...
    score: int#每回合分數，以南北加為基準
    roundNum: int#打牌到第幾輪，0<=roundNum<13
    leadPos: int#每輪第一個出牌的人
    dummyPos:int#夢家方位
    declarerTrick: int#主打方吃的敦數
    defenderTrick: int#防禦方吃的敦數
    playPos: int#換哪個玩家行動
    oneRoundCards: list[int]#每輪打出的牌
    trick: int
    dummyIsLaid: bool
    dummyCards: list[int]
    def __init__(self, p2pInterface: client.p2pInterface, encryption = False, schuffleCheat = False, playCheat = False):
        #建立p2p連線
        self.p2pInterface = p2pInterface
        self.decidePosition()
        self.encryption = encryption
        self.schuffleCheat = schuffleCheat
        self.playCheat = playCheat
        if encryption:
            self.procotocol = Protocol(Pos=self.Pos, nPlayer=4, nCards=52)

    def boradInit(self, boardId):#算出牌號，開叫和身價
        def findDealerandVul(boardId):     
                dealer=boardId%4
                match boardId%16+1:
                    case 1 | 8 | 11 | 14:
                        vul = 0
                    case 2 | 5 | 12 | 5:
                        vul = 1
                    case 3 | 6 | 9 | 16:
                        vul = 2
                    case 4 | 7 | 10 | 13:
                        vul = 3
                return dealer, vul
        self.boradId = boardId
        self.dealer, self.vul = findDealerandVul(boardId)
    
    def toCardName(self, card:int):
        if card >= 0 and card < len(CardName):
            return CardName[card]
        return -1
    
    def toCardNum(self, card:str):
        card = card.upper()
        if card in CardNum:
            return CardNum[card]
        return -1
    
    def toBidName(self, bid:int):
        if bid >= 0 and bid < len(BidName):   
            return BidName[bid]
        
    def toBidNum(self, bid:str):
        bid = bid.upper()
        if bid in BidNum:
            return BidNum[bid]
        return -1

    def displayBid(self, bidList:list[int], dealer=0):

        bid_strs = [self.toBidName(b) for b in bidList]
        # Direction labels
        directions = ["N', 'E', 'S', 'W"]
        if not (0 <= dealer < 4):
            raise ValueError(f"Dealer index must be between 0 and 3, got {dealer}")

        # Rotate directions to start from dealer
        rotated_dirs = directions[dealer:] + directions[:dealer]
        print("     ".join(rotated_dirs))

        # Pad the bids list so its length is a multiple of 4
        rem = len(bid_strs) % 4
        if rem:
            bid_strs += [""] * (4 - rem)

        # Print each round of four bids
        for i in range(0, len(bid_strs), 4):
            row = bid_strs[i:i+4]
            print("  ".join(b.ljust(4) for b in row))

    def displayCards(self, cards:list):
        for i in range(3,-1,-1):
            str = f" {SuitName[i]}: "
            for j in range(12,-1,-1):
                if 13*i+j in cards:
                    str += f" {RankName[j]} "
            print(str)
    
    def displayDeal(self, deal:dict):
        print(f'{deal["dealName"]}, roundNum: {deal["roundNum"]}, declarerTrick: {deal["declarerTrick"]}, defenderTrick: {deal["defenderTrick"]}')
        oneRoundCards:list[int] = deal["oneRoundCards"]
        str = ''
        for card in oneRoundCards:
            str+=self.toCardName(card)+' '
        print(str)

    def display(self, isDisplayCards=0, isDisplayBid=0, isDisplayDeal=0, isDisplayDummyCards=0, cards:list[int]=[], bidList:list[int]=[], deal:dict={}, dummyCards:list[int]=[]):
        def clear_terminal():
            if platform.system() == "Windows":
                os.system('cls')
            else:
                os.system('clear')
        clear_terminal()
        if isDisplayDummyCards and self.Pos != self.dummyPos:
            print('dummy cards')
            self.displayCards(dummyCards)
        if isDisplayCards:
            print('your cards')
            self.displayCards(cards)
        if isDisplayBid:
            self.displayBid(bidList)
        if isDisplayDeal:
            self.displayDeal(deal)
        

    def decidePosition(self):#決定自己坐下的位置
        index = self.p2pInterface.getIndex()
        self.Pos=index
        self.nextPos = (self.Pos+1)%4
        self.prevPos = (self.Pos+3)%4
    
    def shuffle(self):
        '''
        有安全洗牌的步驟
        '''
        if self.encryption:
            self.procotocol.shuffle(self.p2pInterface)
            self.procotocol.dealCards(self.p2pInterface)
            self.cards = self.procotocol.cards
            return self.cards
        '''
        沒有安全洗牌的步驟:
        1.第一位玩家自己洗完牌後叫給剩下三人
        '''
        if self.Pos == self.dealer:
            cards = [i for i in range(52)]
            if self.schuffleCheat:
                cmd = int(input('決定你的洗牌方式\n' \
                '1: 正常洗牌\n' \
                '2: 自己拿超好牌\n' \
                '3: 發奇怪的牌'))
                if cmd == 1:
                    random.shuffle(cards)
                elif cmd == 2:
                    t = 0
                    for j in range (12,-1,-1):
                        for i in range(4):
                            cards[t]=13*i+j
                            t += 1
                else:
                    pass
            else:
                random.shuffle(cards)
            msg1 = {
                'type': 'shuffle',
                'cards':cards[13:26]
            }
            self.p2pInterface.sendMsg(msg1, (self.Pos+1)%4)
            msg2 = {
                'type': 'shuffle',
                'cards':cards[26:39]
            }
            self.p2pInterface.sendMsg(msg2, (self.Pos+2)%4)
            msg3 = {
                'type': 'shuffle',
                'cards':cards[39:52]
            }
            self.p2pInterface.sendMsg(msg3, (self.Pos+3)%4)
            
            self.cards = sorted(cards[0:13])
        else:
            msg = self.p2pInterface.recvMsg(type='shuffle')
            cards = [int(card) for card in msg["cards"]]
            self.cards = sorted(cards)
    
    def bid(self):
        
        def isValidBid(bid:int, bidList:list[int]):
            def findLastBid(bidList:list[int]):
                lastBid = -1
                lastBidPos = -1
                double = 0
                for bid in bidList:
                    if bid < 35:
                        lastBid = bid
                        lastBidPos = bidList.index(bid)%4
                        double = 0
                    if bid == 36:
                        double = 1
                    if bid == 37:
                        double = 2
                return lastBid, lastBidPos, double
            lastBid, lastBidPos, double = findLastBid(bidList)
            Pos = len(bidList)%4
            if bid == -1:#invalid bid
                return 0
            if bid == 35:#pass
                return 1
            if bid == 36:#可以X iff 是對手叫牌 且double = 0
                return (lastBidPos+Pos)%2 == 1 and double == 0 and lastBid != -1 
            if bid == 37:#可以X iff 是自己叫牌 且double = 1
                return (lastBidPos+Pos)%2 == 0 and double == 1 and lastBid != -1 
            if lastBid >= bid:
                return 0
            return 1
        
        def findDeal(bidList:list[int], dealer=0):#不檢查叫牌過程是否合法，只輸出最後的合約
            finalBid = -1
            finalPos = 0 #最後叫的人的方位
            double = 0 # 0 if no X, 1 if X, 2 if XX
            #找最後的叫品
            i = 0
            for bid in bidList:
                if bid < 35:
                    finalBid = bid
                    finalPos = i%4
                    double = 0
                if bid == 36:
                    double = 1
                if bid == 37:
                    double = 2
                i += 1
            if finalBid == -1:
                return -1, -1, -1, 0
            #找到莊家
            i = 0
            declarerPos = -1
            for bid in bidList:
                if  i == finalPos or i == (finalPos+2)%4:
                    if bid < 35 and bid%5 == finalBid%5:
                        declarerPos = (i+dealer)%4
                        break
                i = (i+1)%4
            level = finalBid//5
            trump = finalBid%5
            return level, trump, declarerPos, double
    
        def isBidFinish(bidList:list[int]):
            if len(bidList) < 4:
                return 0
            if bidList[-1] == 35 and bidList[-2] == 35 and bidList[-3] == 35:#連續三個p
                return 1
            return 0
            
        def getDealName(level:int, trump:int, declarerPos:int, double:int):
            if level == -1:
                return 'AP'
            return f'{LevelName[level]}{TrumpsName[trump]}{PostionName[declarerPos]}{DoubleName[double]}'
        
        def bidOne(bidList:list[int]):
            bid = input('叫牌')
            bid = self.toBidNum(bid)
            while not isValidBid(bid, bidList):
                bid = input('叫品不合法，請重新叫牌')
                bid = self.toBidNum(bid)
            bidList.append(bid)
            return bid

        bidList = []
        self.display(isDisplayBid=1, bidList=bidList, isDisplayCards=1, cards=self.cards)
        if self.Pos == self.dealer:
            bid = bidOne(bidList)
            
            msg = {
                'type': 'bid',
                'bid': bid,
                'from': self.Pos,
                'next': self.nextPos,
            }
            self.p2pInterface.sendMsg(msg)
        
        while True:
            self.display(isDisplayBid=1, bidList=bidList, isDisplayCards=1, cards=self.cards)

            msg = self.p2pInterface.recvMsg()
            bidList.append(int(msg["bid"]))

            self.display(isDisplayBid=1, bidList=bidList, isDisplayCards=1, cards=self.cards)
            if int(msg["next"]) == -1:#叫牌結束
                self.level      = int(msg["deal"]["level"])
                self.trump      = int(msg["deal"]["trump"])
                self.declarerPos   = int(msg["deal"]["declarerPos"])
                self.double     = int(msg["deal"]["double"])
                self.dealName   = msg["deal"]["dealName"]
                break
            if int(msg["next"]) == self.Pos:##輪到自己叫牌
                bid = bidOne(bidList)
                if isBidFinish(bidList):
                    self.level, self.trump, self.declarerPos, self.double = findDeal(bidList, self.dealer)
                    self.dealName = getDealName(self.level, self.trump, self.declarerPos, self.double)
                    msg = {
                        'type': 'bidOver',
                        'bid': bid,
                        'from': self.Pos,
                        'next': -1,
                        'deal': {
                            'level': self.level,
                            'trump': self.trump,
                            'declarerPos': self.declarerPos,
                            'leader': (self.declarerPos+1)%4,
                            'double': self.double,
                            'dealName': self.dealName,
                        }
                    }
                    self.p2pInterface.sendMsg(msg)
                    break
                else:
                    msg = {
                        'type': 'bid',
                        'bid': bid,
                        'from': self.Pos,
                        'next': self.nextPos,
                    }
                    self.p2pInterface.sendMsg(msg)
            
    
    def play(self):
        '''
        leadPos: 出牌的玩家
        trump: 王牌
        leadSuit: 出牌的花色
        playerType: 0 莊家 1 防家 2 夢家
        playerPos: 0 N 1 E 2 S 3 W
        declarerTrick: 莊家贏的墩數
        defenderTrick: 防家贏的墩數
        roundNum: 第幾輪
        '''
        def isValidCard(card:int, cards:list[int], oneRoundCards:list[int]):
            if card not in cards:
                return 0
            #檢查是否手上有和第一個出牌一樣的花色但沒出
            if len(oneRoundCards) == 0:
                return 1
            leadSuit = oneRoundCards[0] // 13
            if card//13 == leadSuit:
                return 1
            for c in cards:
                if c//13 == leadSuit:
                    return 0
            return 1
        
        def compare4Cards(cards:list, trump:int, leadPos:int = 0):
            def compare2Cards(card1:int, card2:int, trump:int, leadSuit:int):#0 if card1 is bigger than card2
                suit1 = card1 // 13
                num1 = card1 % 13
                suit2 = card2 // 13
                num2 = card2 % 13
                if suit1 == suit2:
                    if num1>num2:
                        return 0
                    else:
                        return 1
                elif suit1 == trump:
                    return 0
                elif suit2 == trump:
                    return 1
                elif leadSuit == suit1:
                    return 0
                else:
                    return 1
            leadSuit = cards[0] // 13
            maxCard = cards[0]
            maxCardId = 0
            for i in range(1, len(cards)):
                if compare2Cards(maxCard, cards[i], trump, leadSuit) == 1:
                    maxCard = cards[i]
                    maxCardId = i
            return (maxCardId + leadPos)%4

        def play13Rounds():
            if self.dealName == 'AP':
                return
            for self.roundNum in range(13):
                playOneRound()

        def dummyLaid():

            if self.Pos == self.dummyPos:
                msg = {
                    'type': 'laid',
                    'dummyCards': self.cards,
                    'from': self.Pos,
                }
                self.p2pInterface.sendMsg(msg, peerIndex = -1)
            else:
                msg = self.p2pInterface.recvMsg(type='laid')
                self.dummyCards = msg["dummyCards"]
                self.dummyCards = [int(card) for card in self.dummyCards]
                self.dummyIsLaid = True
                return
        
        def playOneRound():
            self.playPos = self.leadPos
            self.oneRoundCards = []
            for _ in range(4):
                if _ == 1 and self.roundNum==0:#夢家攤牌
                    dummyLaid()
                #顯示畫面
                self.display(isDisplayCards=1, cards=self.cards, isDisplayDummyCards=self.dummyIsLaid, dummyCards=self.dummyCards, isDisplayDeal=1, 
                deal={
                    'roundNum': self.roundNum,
                    'declarerTrick': self.declarerTrick,
                    'defenderTrick': self.defenderTrick,
                    'dealName': self.dealName,
                    'oneRoundCards': self.oneRoundCards
                })
                
                #出牌
                if self.Pos == self.playPos:
                    playOneCard()
                else:
                    otherPlayOneCard()
                if self.playPos == self.dummyPos and self.Pos != self.dummyPos:
                    self.dummyCards.remove(self.oneRoundCards[-1])
                self.playPos = (self.playPos+1)%4
            #每圈結算s
            winner = compare4Cards(self.oneRoundCards, self.trump, self.leadPos)
            self.leadPos = winner
            self.trick += (winner+self.Pos)%2 == 0
            self.declarerTrick += (winner+self.declarerPos)%2 == 0
            self.defenderTrick += (winner+self.declarerPos)%2 != 0

        def playOneCard():
            #決定card_val
            if self.Pos == self.dummyPos:#叫莊家決定
                msg = {
                    'type': 'dummy',
                    'dummyCards': self.cards,
                    'oneRoundCards': self.oneRoundCards,
                    'from': self.Pos
                }
                self.p2pInterface.sendMsg(msg, peerIndex = self.declarerPos)
                msg = self.p2pInterface.recvMsg('declare')
                card_val = int(msg["card"])
            else:
                card_val = input('請出牌')
                card_val = self.toCardNum(card_val)
                while not isValidCard(card_val, self.cards, self.oneRoundCards):
                    card_val = input('請重新出牌')
                    card_val = self.toCardNum(card_val)
            if self.encryption:#如果有加密功能，叫其他人驗證
                ok = self.procotocol.playCards(self.p2pInterface, card_val)
                if not ok:
                    print("牌被多人质疑！中断本轮出牌。")
                    return -1
            else:#否則單純送出資料
                self.p2pInterface.sendMsg(
                    {
                        'type': 'play card',
                        'Pos': self.Pos,
                        'card_val':card_val
                    }, peerIndex=-1
                )
            self.cards.remove(card_val)
            self.oneRoundCards.append(card_val)
            return
        
        def otherPlayOneCard():
            if self.Pos == self.declarerPos and self.playPos == self.dummyPos:#幫莊家出牌
                msg =self.p2pInterface.recvMsg(type='dummy')
                dummycards = msg["dummyCards"]
                dummycards = [int(card) for card in dummycards]
                card_val = self.toCardNum(input('請幫夢家出牌'))
                while not isValidCard(card_val, dummycards, self.oneRoundCards):
                    card_val = self.toCardNum(input('請重新出牌'))
                msg = {
                    'type': 'declare',
                    'card': card_val,
                    'from': self.Pos,
                }
                self.p2pInterface.sendMsg(msg, peerIndex = self.dummyPos)
            if self.encryption:#如果有加密功能，則驗證其他人的牌
                card_val, sender = self.procotocol.otherplayCards(self.p2pInterface)
                if card_val == -1 or sender != self.playPos:
                    return -1
            else:
                msg = self.p2pInterface.recvMsg(type='play card')
                card_val = msg["card_val"]
            self.oneRoundCards.append(card_val)
            return
            
        def initPlay():
            self.leadPos = (self.declarerPos+1)%4
            self.roundNum = 0
            self.declarerTrick = 0
            self.defenderTrick = 0
            self.trick = 0
            self.trump = self.trump
            self.vul = self.vul
            self.dummyPos = (self.declarerPos+2)%4
            self.dummyIsLaid = False
            self.dummyCards = []

        def calculateScore(level, trump, declarerPos, vul, double, declarerTrick):
            #要吃敦數=level+7, level=0,...,6
            #trump:nt=4,s=3,h=2,d=1,c=0
            #double:none=0,x=1,xx=2
            def isVul(declarerPos, vul):
                if declarerPos == 0 or declarerPos == 2:
                    return vul == 1 or vul == 3
                else:
                    return vul ==2 or vul == 3
            if level == -1:#AP
                return 0
            vulnerable = isVul(declarerPos, vul)

            contractTricks = level + 7
            made = declarerTrick >= contractTricks
            score = 0

            # Trick score per trick
            if trump == 4:
                base_trick = 40 if level >= 0 else 0
                # for NT: first trick 40, rest 30
                trick_vals = [40] + [30] * level
            else:
                per = 20 if trump < 2 else 30
                trick_vals = [per] * (level + 1)

            # If contract is made
            if made:
                # contract trick points (no overtricks)
                trick_score = sum(trick_vals)
                # apply doubling
                trick_score *= (1 << double)
                score += trick_score
                # insult bonus
                if double == 1:
                    score += 50
                elif double == 2:
                    score += 100
                # overtricks
                over = declarerTrick - contractTricks
                if double == 0:
                    # undoubled overtricks at trick_vals[-1]
                    score += over * trick_vals[-1]
                else:
                    # doubled/rdouble overtricks fixed amount
                    rate = 100 if not vulnerable else 200
                    rate *= (1 << (double - 1))
                    score += over * rate
                # part or game bonus
                if trick_score >= 100:
                    score += 500 if vulnerable else 300
                else:
                    score += 50
                # slam bonus
                if level == 5:  # small slam
                    score += 750 if vulnerable else 500
                elif level == 6:  # grand slam
                    score += 1500 if vulnerable else 1000
            else:
                # undertricks
                under = contractTricks - declarerTrick
                if double == 0:
                    penalty = 100 * under if vulnerable else 50 * under
                else:
                    penalty = 0
                    if not vulnerable:
                        # 100,200,300+ progression
                        for i in range(under):
                            if i == 0:
                                penalty += 100
                            elif i < 3:
                                penalty += 200
                            else:
                                penalty += 300
                    else:
                        # 200,300+ progression
                        for i in range(under):
                            penalty += 200 if i == 0 else 300
                    penalty *= double == 2 and 2 or 1  # redouble doubles penalty
                score -= penalty
            #分數是以南北家為基準
            if declarerPos == 1 or declarerPos == 3:
                score = -score
            return score
        
        def settleScore():
            if self.Pos == self.dealer:
                self.score = calculateScore(self.level, self.trump, self.declarerPos, self.vul, self.double, self.declarerTrick)
                msg = {
                    'type': 'result',
                    'deal': {
                        'boradId': self.boradId,
                        'level': self.level,
                        'trump': self.trump,
                        'declarerPos': self.declarerPos,
                        'double':self.double,
                        'vul':self.vul,
                        'declarerTrick': self.declarerTrick,
                        'score': self.score
                    }
                }
                self.p2pInterface.sendMsg(msg)
                print(self.score)
            else:
                msg = self.p2pInterface.recvMsg(type='result')
                self.score = int(msg["deal"]["score"])
                print(self.score)
                    
        initPlay()
        play13Rounds()
        settleScore()
  
    def run(self):
        for i in range(8):
            self.boradInit(i)
            self.shuffle()
            self.bid()
            self.play()

if __name__=='__main__':
    '''
    isSignature:是否使用簽章
    encryption:是否使用mental poker洗牌方式
    schuffleCheat:啟用的話玩家可以在洗牌嘗試作弊
    playCheat:啟用的化玩家可以在出牌嘗試作弊
    '''
    
    
    p2pInterface = client.p2pInterface(isSignature = True)
    bridge = Bridge(p2pInterface=p2pInterface, encryption = True, schuffleCheat = True, playCheat = True)
    bridge.run()