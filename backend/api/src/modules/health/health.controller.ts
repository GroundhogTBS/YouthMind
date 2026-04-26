import { Controller, Get } from '@nestjs/common';
import { Public } from '../../common/decorators/public.decorator';

@Controller('health')
export class HealthController {
  @Public()
  @Get()
  check() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'youthmind-api'
    };
  }

  @Public()
  @Get('ready')
  ready() {
    return { ready: true };
  }
}
