import { Controller, Post, Get, Body, Param, Query, Request } from '@nestjs/common';
import { ChatService } from './chat.service';

interface RequestUser {
  sub: number;
  phone: string;
  userType: string;
}

interface RequestWithUser extends Request {
  user: RequestUser;
}

@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post('session')
  async createSession(@Request() req: RequestWithUser) {
    return this.chatService.createSession(req.user.sub);
  }

  @Get('sessions')
  async getSessions(@Request() req: RequestWithUser) {
    return this.chatService.getSessions(req.user.sub);
  }

  @Get('session/:id')
  async getSession(@Request() req: RequestWithUser, @Param('id') id: string) {
    return this.chatService.getSession(parseInt(id, 10), req.user.sub);
  }

  @Get('messages/:sessionId')
  async getMessages(
    @Request() req: RequestWithUser,
    @Param('sessionId') sessionId: string,
    @Query('limit') limit?: string
  ) {
    return this.chatService.getMessages(
      parseInt(sessionId, 10),
      req.user.sub,
      limit ? parseInt(limit, 10) : 50
    );
  }

  @Post('send/:sessionId')
  async sendMessage(
    @Request() req: RequestWithUser,
    @Param('sessionId') sessionId: string,
    @Body() body: { content: string }
  ) {
    return this.chatService.sendMessage(parseInt(sessionId, 10), req.user.sub, body.content);
  }
}
