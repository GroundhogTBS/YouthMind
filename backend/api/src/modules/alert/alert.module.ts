import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AlertEvent } from './alert-event.entity';
import { AlertService } from './alert.service';
import { AlertController } from './alert.controller';

@Module({
  imports: [TypeOrmModule.forFeature([AlertEvent])],
  controllers: [AlertController],
  providers: [AlertService],
  exports: [AlertService]
})
export class AlertModule {}
