import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Session } from './session.entity';
import { Message } from './message.entity';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

@Injectable()
export class ChatService {
  private aiServiceUrl: string;

  constructor(
    @InjectRepository(Session)
    private sessionRepository: Repository<Session>,
    @InjectRepository(Message)
    private messageRepository: Repository<Message>,
    private configService: ConfigService
  ) {
    this.aiServiceUrl = this.configService.get('AI_SERVICE_URL', 'http://localhost:9000');
  }

  async createSession(userId: number) {
    const session = this.sessionRepository.create({ userId });
    return this.sessionRepository.save(session);
  }

  async getSessions(userId: number) {
    return this.sessionRepository.find({
      where: { userId },
      order: { createdAt: 'DESC' }
    });
  }

  async getSession(sessionId: number, userId: number) {
    return this.sessionRepository.findOne({
      where: { id: sessionId, userId }
    });
  }

  async getMessages(sessionId: number, userId: number, limit = 50) {
    return this.messageRepository.find({
      where: { sessionId, userId },
      order: { createdAt: 'ASC' },
      take: limit
    });
  }

  async sendMessage(sessionId: number, userId: number, content: string) {
    const session = await this.getSession(sessionId, userId);
    if (!session) {
      throw new Error('会话不存在');
    }

    const userMessage = this.messageRepository.create({
      sessionId,
      userId,
      content,
      sender: 'user'
    });
    await this.messageRepository.save(userMessage);

    const context = await this.getMessages(sessionId, userId, 10);
    const aiResponse = await this.callAIService(context, content);

    const botMessage = this.messageRepository.create({
      sessionId,
      userId,
      content: aiResponse.content,
      sender: 'bot',
      emotion: typeof aiResponse.emotion === 'object' ? JSON.stringify(aiResponse.emotion) : aiResponse.emotion,
      emotionScore: aiResponse.emotionScore
    });
    await this.messageRepository.save(botMessage);

    await this.sessionRepository.update(sessionId, {
      messageCount: session.messageCount + 2,
      lastMessageAt: new Date()
    });

    return {
      userMessage,
      botMessage,
      alert: aiResponse.alert
    };
  }

  private async callAIService(context: Message[], content: string) {
    try {
      const response = await axios.post(`${this.aiServiceUrl}/ai/chat/send`, {
        session_id: 'default',
        content: content,
        user_info: { language: 'zh' }
      });

      return {
        content: response.data.content,
        emotion: response.data.emotion,
        emotionScore: response.data.emotion?.confidence || 0.5,
        alert: response.data.alert || false
      };
    } catch (error) {
      console.error('AI Service Error:', error);
      return {
        content: '抱歉，我现在有点累，请稍后再和我聊聊吧。如果需要帮助，也可以拨打心理援助热线：400-161-9995',
        emotion: { primary: 'neutral', confidence: 0.5 },
        emotionScore: 0.5,
        alert: false
      };
    }
  }
}
