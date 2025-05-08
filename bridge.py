import random
# card id
#0-12 club, 13-25 diamond, 26-38 heart, 39-51 spade
#0 spades A, 1 spades 2,...
# card num
# 2 = 0, 3 = 1, ..., 10 = 8, J = 9, Q = 10, K = 11, A = 12

#N=0,E=1,S=2,W=3
#vul:0 none,1 ns,2 ew,3 both
#boardId從1開始

class bridge:#紀錄一牌的資訊，包含叫牌和打牌
    def __init__(self, boardId, position):
        self.boardId = boardId
        self.dealer, self.vul = self.findDealerandVul(boardId)
        self.position = position
        #叫牌
        self.biddingList = []
        #打牌
        
    def findDealerandVul(self,boardId):
        boardId=(boardId-1)%16+1
        dealer=(boardId-1)%4
        match boardId:
            case 1 | 8 | 11 | 14:
                vul = 0
            case 2 | 5 | 12 | 5:
                vul = 1
            case 3 | 6 | 9 | 16:
                vul = 2
            case 4 | 7 | 10 | 13:
                vul = 3
        return dealer, vul
    def shuffleCards(self):
        cards=[i for i in range(52)]
        random.shuffle(cards)
        return cards
    def compare2Cards(self, card1:int, card2:int, trump:int, leadSuit:int):#0 if card1 is bigger than card2
        suit1, num1 = self.getSuitandNum(card1)
        suit2, num2 = self.getSuitandNum(card2)
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
    def getSuitandNum(card:int):
        suit = card // 13
        num = (card-1) % 13
        return suit, num
    def compare4Cards(self, cards:list, trump:int, leadSuit:int):
        maxCard = cards[0]
        maxCardId = 0
        for i in range(1, len(cards)):
            if self.compare2Cards(maxCard, cards[i], trump, leadSuit) == 1:
                maxCard = cards[i]
                maxCardId = i
        return maxCardId

class board(bridge):
    pass
