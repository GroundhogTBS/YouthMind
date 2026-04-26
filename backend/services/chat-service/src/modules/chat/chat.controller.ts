import { Controller, Get, Post, Put, Delete, Body, Param, Headers, UnauthorizedException } from '@nestjs/common';
import { ChatService } from './chat.service';
import { JwtService } from '@nestjs/jwt';

@Controller('chat')
export class ChatController {
  constructor(
    private readonly chatService: ChatService,
    private readonly jwtService: JwtService,
  ) {}

  private getUserId(authHeader: string): number {
    if (!authHeader) {
      throw new UnauthorizedException('未登录');
    }
    const token = authHeader.replace('Bearer ', '');
    const payload = this.jwtService.verify(token);
    return payload.userId;
  }

  @Post('session')
  async createSession(@Headers('authorization') auth: string) {
    const userId = this.getUserId(auth);
    return this.chatService.createSession(userId);
  }

  @Get('sessions')
  async getSessions(@Headers('authorization') auth: string) {
    const userId = this.getUserId(auth);
    return this.chatService.getSessions(userId);
  }

  @Get('session/:id')
  async getSession(@Param('id') id: string, @Headers('authorization') auth: string) {
    const userId = this.getUserId(auth);
    return this.chatService.getSession(Number(id), userId);
  }

  @Put('session/:id/title')
  async updateTitle(
    @Param('id') id: string,
    @Body('title') title: string,
    @Headers('authorization') auth: string,
  ) {
    const userId = this.getUserId(auth);
    await this.chatService.updateSessionTitle(Number(id), userId, title);
    return { success: true };
  }

  @Delete('session/:id')
  async deleteSession(@Param('id') id: string, @Headers('authorization') auth: string) {
    const userId = this.getUserId(auth);
    await this.chatService.deleteSession(Number(id), userId);
    return { success: true };
  }

  @Post('session/:id/message')
  async sendMessage(
    @Param('id') id: string,
    @Body('content') content: string,
    @Headers('authorization') auth: string,
  ) {
    const userId = this.getUserId(auth);
    return this.chatService.sendMessage(Number(id), userId, content);
  }

  @Get('health')
  health() {
    return { status: 'ok', service: 'chat-service' };
  }
}
