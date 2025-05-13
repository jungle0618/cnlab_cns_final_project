import random
import client
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
    index: int
    nextIndex: int
    boradId: int
    dealer: int
    vul: int
    cards: list[int]
    level: int
    trump: int
    declarer: int
    double: int
    dealName: str
    score: int
    roundNum: int
    leadPos: int
    dummy:int
    declarerTrick: int
    defenderTrick: int
    def __init__(self):
        #建立p2p連線
        super().__init__()

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
        directions = ['N', 'E', 'S', 'W']
        if not (0 <= dealer < 4):
            raise ValueError(f"Dealer index must be between 0 and 3, got {dealer}")

        # Rotate directions to start from dealer
        rotated_dirs = directions[dealer:] + directions[:dealer]
        print("     ".join(rotated_dirs))

        # Pad the bids list so its length is a multiple of 4
        rem = len(bid_strs) % 4
        if rem:
            bid_strs += [''] * (4 - rem)

        # Print each round of four bids
        for i in range(0, len(bid_strs), 4):
            row = bid_strs[i:i+4]
            print("  ".join(b.ljust(4) for b in row))

    def displayCards(self, cards:list):
        for i in range(3,-1,-1):
            str = f'{SuitName[i]}: '
            for j in range(12,-1,-1):
                if 13*i+j in cards:
                    str += f'{RankName[j]}'
            print(str)
    
    def display(self, isDisplayCards=0, isDisplayBid=0, isDisplayDeal=0, cards:list[int]=[], bidList:list[int]=[]):
        def clear_terminal():
            # 判斷作業系統
            if platform.system() == "Windows":
                os.system('cls')  # Windows 系統清除
            else:
                os.system('clear')  # Linux / macOS 清除
        clear_terminal()
        if isDisplayCards:
            self.displayCards(cards)
        if isDisplayBid:
            self.displayBid(bidList)

    def decidePosition(self):#決定自己坐下的位置
        index = self.getIndex()
        self.Pos=index
        self.nextPos = (self.Pos+1)%4
    
    def shuffle(self):
        '''
        1.每個人洗完牌後交給下一個人
        2.最後一個人洗完牌後交給第一個人(先懶的寫)
        '''
        if self.Pos == self.dealer:
            cards = [i for i in range(52)]
            #random.shuffle(cards)
            msg = {
                'cards':cards
            }       
            self.sendMsg(msg, peerIndex = self.nextPos)
            msg = self.recvMsg()
            cards = [int(card) for card in msg['cards']]
            msg1 = {
                'cards':cards[13:26]
            }
            self.sendMsg(msg1, (self.Pos+1)%4)
            msg2 = {
                'cards':cards[26:39]
            }
            self.sendMsg(msg2, (self.Pos+2)%4)
            msg3 = {
                'cards':cards[39:52]
            }
            self.sendMsg(msg3, (self.Pos+3)%4)
            
            self.cards = sorted(cards[0:13])
        else:
            msg = self.recvMsg()
            cards = [int(card) for card in msg['cards']]
            random.shuffle(cards)
            msg = {
                'cards':cards
            }
            self.sendMsg(msg, peerIndex = self.nextPos)
            msg = self.recvMsg()
            cards = [int(card) for card in msg['cards']]
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
            declarer = -1
            for bid in bidList:
                print(i, bid, finalBid, dealer)
                if  i == finalPos or i == (finalPos+2)%4:
                    if bid < 35 and bid%5 == finalBid%5:
                        declarer = (i+dealer)%4
                        break
                i = (i+1)%4
            level = finalBid//5
            trump = finalBid%5
            return level, trump, declarer, double
    
        def isBidFinish(bidList:list[int]):
            if len(bidList) < 4:
                return 0
            if bidList[-1] == 35 and bidList[-2] == 35 and bidList[-3] == 35:#連續三個p
                return 1
            return 0
            
        def getDealName(level:int, trump:int, declarer:int, double:int):
            if level == -1:
                return 'AP'
            return f'{LevelName[level]}{TrumpsName[trump]}{PostionName[declarer]}{DoubleName[double]}'
        
        def bidOne(bidList:list[int]):
            bid = input('叫牌')
            bid = self.toBidNum(bid)
            while not isValidBid(bid, bidList):
                bid = input('叫品不合法，請重新叫牌')
                bid = self.toBidNum(bid)
            bidList.append(bid)
        
        if self.Pos == self.dealer:
            bidList = []
            bidOne(bidList)
            msg = {
                'bidList': bidList,
                'from': self.Pos,
                'next': self.nextPos,
            }
            self.sendMsg(msg)

        while True:
            msg = self.recvMsg()
            bidList = msg['bidList']
            bidList = [int(bid) for bid in bidList]
            self.display(isDisplayBid=1, bidList=bidList, isDisplayCards=1, cards=self.cards)
            if int(msg['next']) == self.Pos:##輪到自己叫牌
                bidOne(bidList)
                if isBidFinish(bidList):
                    self.level, self.trump, self.declarer, self.double = findDeal(bidList, self.dealer)
                    self.dealName = getDealName(self.level, self.trump, self.declarer, self.double)
                    msg = {
                        'bidList': bidList,
                        'from': self.Pos,
                        'next': -1,
                        'deal': {
                            'level': self.level,
                            'trump': self.trump,
                            'declarer': self.declarer,
                            'leader': (self.declarer+1)%4,
                            'double': self.double,
                            'dealName': self.dealName,
                        }
                    }
                    self.sendMsg(msg)
                    break
                else:
                    msg = {
                        'bidList': bidList,
                        'from': self.Pos,
                        'next': self.nextPos,
                    }
                    self.sendMsg(msg)
            if int(msg['next']) == -1:#叫牌結束
                self.level      = int(msg['deal']['level'])
                self.trump      = int(msg['deal']['trump'])
                self.declarer   = int(msg['deal']['declarer'])
                self.double     = int(msg['deal']['double'])
                self.dealName   = msg['deal']['dealName']
                break
    
    def play(self):
        '''
        leadPos: 出牌的玩家
        trump: 王牌
        leadSuit: 出牌的花色
        playerType: 0 莊家 1 防家 2 夢家
        playerPos: 0 N 1 E 2 S 3 W
        declarerTrick: 莊家贏的墩數
        defenderTrick: 防家贏的墩數
        round: 第幾輪
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
                print(f'winner: {self.leadPos}')
        def playOneRound():
            print(f'第{self.roundNum+1}輪')
            print(f'吃到的敦數: {self.trick}')
            self.display(isDisplayCards=1, cards=self.cards)
            if self.leadPos == self.Pos:
                oneRoundCards = []
                playOneCard(oneRoundCards)
                msg = {
                    'type': 'play',
                    'oneRoundCards': oneRoundCards,
                    'roundNum': self.roundNum,
                    'from': self.Pos,
                    'next': self.nextPos,
                }
                self.sendMsg(msg)
            while True:
                msg = self.recvMsg()
                if self.roundNum == 0 and self.Pos == self.dummy and msg['next'] == self.Pos:#夢家攤牌
                    dummyLaid()
                
                if msg['type'] == 'play':# 其他人出牌
                    oneRoundCards = msg['oneRoundCards']
                    oneRoundCards = [int(card) for card in oneRoundCards]
                    if int(msg['next']) == self.Pos:
                        playOneCard(oneRoundCards)
                        if len(oneRoundCards) == 4:
                            winner = compare4Cards(oneRoundCards, self.trump, self.leadPos)
                            self.leadPos = winner
                            self.trick += (winner+self.Pos)%2 == 0
                            self.declarerTrick += (winner+self.declarer)%2 == 0
                            self.defenderTrick += (winner+self.declarer)%2 != 0
                            msg = {
                                'type': 'play',
                                'oneRoundCards': oneRoundCards,
                                'roundNum': self.roundNum,
                                'from': self.Pos,
                                'next': -1,
                                'winner': winner,
                            }
                            self.sendMsg(msg)
                            break
                        else:
                            msg = {
                                'type': 'play',
                                'oneRoundCards': oneRoundCards,
                                'roundNum': self.roundNum,
                                'from': self.Pos,
                                'next': self.nextPos,
                            }
                            self.sendMsg(msg)
                    elif len(oneRoundCards) == 4:#結算
                        winner = int(msg['winner'])
                        self.leadPos = winner
                        self.trick += (winner+self.Pos)%2 == 0
                        self.declarerTrick += (winner+self.declarer)%2 == 0
                        self.defenderTrick += (winner+self.declarer)%2 != 0
                        break
                if msg['type'] == 'dummy' and self.Pos == self.declarer:#幫夢家出牌
                    oneRoundCards = msg['oneRoundCards']
                    oneRoundCards = [int(card) for card in oneRoundCards]
                    dummycards = msg['dummyCards']
                    dummycards = [int(card) for card in dummycards]
                    card = self.toCardNum(input('請幫夢家出牌'))
                    while not isValidCard(card, dummycards, oneRoundCards):
                        card = self.toCardNum(input('請重新出牌'))
                    msg = {
                        'type': 'dummy',
                        'card': card,
                        'from': self.Pos,
                        'next': -1,
                    }
                    self.sendMsg(msg, peerIndex = self.dummy)
                if msg['type'] == 'laid':
                    pass

        def dummyLaid():
            assert self.Pos == self.dummy
            msg = {
                'type': 'laid',
                'dummyCards': self.cards,
                'from': self.Pos,
                'next': -1,
            }
            self.sendMsg(msg)

        def playOneCard(oneRoundCards:list[int]):
            if self.Pos == self.dummy:#叫莊家決定
                msg = {
                    'type': 'dummy',
                    'dummyCards': self.cards,
                    'oneRoundCards': oneRoundCards,
                    'from': self.Pos,
                    'next': self.declarer,
                }
                self.sendMsg(msg, peerIndex = self.declarer)
                msg = self.recvMsg()
                card = int(msg['card'])
                self.cards.remove(card)
                oneRoundCards.append(card)
                return
            card = input('請出牌')
            card = self.toCardNum(card)
            while not isValidCard(card, self.cards, oneRoundCards):
                card = input('請重新出牌')
                card = self.toCardNum(card)
            self.cards.remove(card)
            oneRoundCards.append(card)
            return
        
        def initPlay():
            self.leadPos = (self.declarer+1)%4
            self.roundNum = 0
            self.declarerTrick = 0
            self.defenderTrick = 0
            self.trick = 0
            self.trump = self.trump
            self.vul = self.vul
            self.dummy = (self.declarer+2)%4

        def calculateScore(level, trump, declarer, vul, double, declarerTrick):
            #要吃敦數=level+7, level=0,...,6
            #trump:nt=4,s=3,h=2,d=1,c=0
            #double:none=0,x=1,xx=2
            def isVul(declarer, vul):
                if declarer == 0 or declarer == 2:
                    return vul == 1 or vul == 3
                else:
                    return vul ==2 or vul == 3
            if level == -1:#AP
                return 0
            vulnerable = isVul(declarer, vul)

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
            if declarer == 1 or declarer == 3:
                score = -score
            return score
        
        def settleScore():
            if self.Pos == self.declarer:
                self.score = calculateScore(self.level, self.trump, self.declarer, self.vul, self.double, self.declarerTrick)
                msg = {
                    'type': 'result',
                    'deal': {
                        'boradId': self.boradId,
                        'level': self.level,
                        'trump': self.trump,
                        'declarer': self.declarer,
                        'double':self.double,
                        'vul':self.vul,
                        'declarerTrick': self.declarerTrick,
                        'score': self.score
                    }
                }
                self.sendMsg(msg)
                print(self.score)
            else:
                msg = self.recvMsg()
                self.score = int(msg['deal']['score'])
                print(self.score)
                    
        initPlay()
        play13Rounds()
        settleScore()
  
    def run(self):
        self.decidePosition()
        for i in range(8):
            self.boradInit(i)
            print(self.boradId, self.dealer)
            self.shuffle()
            self.bid()
            print(self.dealName)
            self.play()

if __name__=='__main__':
    bridge = Bridge()
    bridge.run()