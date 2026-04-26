import { Controller, Post, Get, Put, Body, Request } from '@nestjs/common';
import { UserService } from './user.service';
import { Public } from '../../common/decorators/public.decorator';

interface RequestUser {
  sub: number;
  phone: string;
  userType: string;
}

interface RequestWithUser extends Request {
  user: RequestUser;
}

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Public()
  @Post('register')
  async register(@Body() body: { phone: string; password: string; nickname?: string }) {
    return this.userService.register(body.phone, body.password, body.nickname);
  }

  @Public()
  @Post('login')
  async login(@Body() body: { phone: string; password: string }) {
    return this.userService.login(body.phone, body.password);
  }

  @Get('profile')
  async getProfile(@Request() req: RequestWithUser) {
    return this.userService.getProfile(req.user.sub);
  }

  @Put('profile')
  async updateProfile(@Request() req: RequestWithUser, @Body() body: Record<string, unknown>) {
    return this.userService.updateProfile(req.user.sub, body as any);
  }
}
