import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ChatSession, ChatMessage } from './entities/chat.entity';
import axios from 'axios';

@Injectable()
export class ChatService {
  private readonly aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:9000';

  constructor(
    @InjectRepository(ChatSession)
    private sessionRepository: Repository<ChatSession>,
    @InjectRepository(ChatMessage)
    private messageRepository: Repository<ChatMessage>,
  ) {}

  async createSession(userId: number): Promise<ChatSession> {
    const session = this.sessionRepository.create({ userId });
    return this.sessionRepository.save(session);
  }

  async getSessions(userId: number): Promise<ChatSession[]> {
    return this.sessionRepository.find({
      where: { userId, isActive: true },
      order: { updatedAt: 'DESC' },
    });
  }

  async getSession(sessionId: number, userId: number): Promise<ChatSession | null> {
    return this.sessionRepository.findOne({
      where: { id: sessionId, userId },
      relations: ['messages'],
    });
  }

  async updateSessionTitle(sessionId: number, userId: number, title: string): Promise<void> {
    await this.sessionRepository.update({ id: sessionId, userId }, { title });
  }

  async deleteSession(sessionId: number, userId: number): Promise<void> {
    await this.sessionRepository.update({ id: sessionId, userId }, { isActive: false });
  }

  async sendMessage(sessionId: number, userId: number, content: string): Promise<ChatMessage> {
    const session = await this.sessionRepository.findOne({
      where: { id: sessionId, userId },
    });
    
    if (!session) {
      throw new Error('会话不存在');
    }

    const userMessage = this.messageRepository.create({
      sessionId,
      role: 'user',
      content,
    });
    await this.messageRepository.save(userMessage);

    const messages = await this.messageRepository.find({
      where: { sessionId },
      order: { createdAt: 'ASC' },
    });

    const aiResponse = await this.callAIService(messages);
    
    const assistantMessage = this.messageRepository.create({
      sessionId,
      role: 'assistant',
      content: aiResponse.content,
      emotion: aiResponse.emotion,
      emotionScore: aiResponse.emotionScore,
      riskLevel: aiResponse.riskLevel,
    });
    
    await this.messageRepository.save(assistantMessage);
    
    await this.sessionRepository.update(sessionId, {
      title: session.title === '新对话' ? content.slice(0, 20) : session.title,
    });

    return assistantMessage;
  }

  private async callAIService(messages: ChatMessage[]): Promise<any> {
    try {
      const response = await axios.post(`${this.aiServiceUrl}/ai/chat/send`, {
        messages: messages.map(m => ({ role: m.role, content: m.content })),
      });
      
      return {
        content: response.data.content,
        emotion: response.data.emotion?.primary,
        emotionScore: response.data.emotion?.confidence,
        riskLevel: response.data.crisis?.riskLevel,
      };
    } catch (error) {
      console.error('AI Service Error:', error.message);
      return {
        content: '抱歉，我现在无法回应。请稍后再试，或者拨打心理援助热线 400-161-9995。',
        emotion: null,
        emotionScore: null,
        riskLevel: null,
      };
    }
  }
}
