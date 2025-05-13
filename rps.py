#rock=0,paper=5,scissor=2
import client
class Rps(client.p2pInterface):#scissor paper stone
    def __init__(self):
        super().__init__()
    def winner(self,ways):
        hasRock=0
        hasPaper=0
        hasScissor=0
        rock=[]
        paper=[]
        scissor=[]
        for way in ways:
            if way==0:
                hasRock=1
            if way==5:
                hasPaper=1
            else:
                hasScissor=1
        if      hasRock and     hasPaper and not hasScissor:
            return 1 if ways[0]==5 else -1
        if  not hasRock and     hasPaper and     hasScissor:
            return 1 if ways[0]==2 else -1
        if      hasRock and not hasPaper and     hasScissor:
            return 1 if ways[0]==0 else -1
        return 0
    def run(self):
        while True:
            way=int(input('輸入0 or 2 or 5:'))
            message={
                'index':0,
                'way':way
            }
            self.sendMsg(message)
            m1=self.recvMsg()
            id1=int(m1['index'])
            way1=int(m1['way'])
            m2=self.recvMsg()
            id2=int(m2['index'])
            way2=int(m2['way'])
            print(f'玩家 {id1} 出了 {way1}')
            print(f'玩家 {id2} 出了 {way2}')
            print(f'你出了 {way}')
            result=self.winner([way,way1,way2])
            match result:
                case 0:
                    print('平手')
                case 1:
                    print('獲勝')
                case -1:
                    print('失敗')


if __name__=='__main__':
    #inputQueue, outputQueue = client.p2pRun() #建立p2p連線，inputQueue 和 outputQueue 分別為p2p request和response
    rps = Rps()
    rps.run()