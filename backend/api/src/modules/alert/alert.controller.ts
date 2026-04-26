import { Controller, Get, Post, Body, Param, Request } from '@nestjs/common';
import { AlertService } from './alert.service';
import { Public } from '../../common/decorators/public.decorator';

interface RequestUser {
  sub: number;
  phone: string;
  userType: string;
}

interface RequestWithUser extends Request {
  user: RequestUser;
}

@Controller('alert')
export class AlertController {
  constructor(private readonly alertService: AlertService) {}

  @Get('list')
  async getAlerts(@Request() req: RequestWithUser) {
    const userId = req.user.userType === 'admin' ? undefined : req.user.sub;
    return this.alertService.getAlerts(userId);
  }

  @Get('stats')
  async getStats() {
    return this.alertService.getStats();
  }

  @Post('handle/:id')
  async handleAlert(
    @Request() req: RequestWithUser,
    @Param('id') id: string,
    @Body() body: { result: string }
  ) {
    return this.alertService.handleAlert(parseInt(id, 10), req.user.sub, body.result);
  }
}
