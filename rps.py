#rock=0,paper=5,scissor=2
class Rps:#scissor paper stone
    def __init__(self, inputQueue, outputQueue):
        self.inputQueue = inputQueue
        self.outputQueue = outputQueue
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
        if hasRock and hasPaper and not hasScissor:
            return 1 if ways[0]==5 else -1
        if not hasRock and hasPaper and hasScissor:
            return 1 if ways[0]==2 else -1
        if hasRock and not hasPaper and hasScissor:
            return 1 if ways[0]==0 else -1
        return 0
    def run(self):
        while True:
            way=int(input('輸入0 or 2 or 5:'))
            self.sendMsg(f'-1:-1:{way}')
            m1=self.recvMsg()
            m1=m1.split(':')
            id1=int(m1[0])
            way1=int(m1[1])
            m2=self.recvMsg()
            m2=m2.split(':')
            id2=int(m2[0])
            way2=int(m2[1])
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
    def sendMsg(self, msg):
        print(f'rps send [{msg}]')
        self.inputQueue.put(msg)
        return
    def recvMsg(self):
        return self.outputQueue.get()
import client
if __name__=='__main__':
    inputQueue, outputQueue = client.p2pRun()
    rps = Rps(inputQueue, outputQueue)
    rps.run()