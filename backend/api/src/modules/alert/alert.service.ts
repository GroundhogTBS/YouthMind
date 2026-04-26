import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { AlertEvent } from './alert-event.entity';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AlertService {
  constructor(
    @InjectRepository(AlertEvent)
    private alertRepository: Repository<AlertEvent>,
    private configService: ConfigService
  ) {}

  async createAlert(data: {
    userId: number;
    alertLevel: string;
    alertType: string;
    triggerSource: string;
    triggerContent?: string;
    triggerKeywords?: string;
    riskScore?: number;
  }) {
    const alert = this.alertRepository.create(data);
    return this.alertRepository.save(alert);
  }

  async getAlerts(userId?: number, status?: string) {
    const query = this.alertRepository.createQueryBuilder('alert');
    
    if (userId) {
      query.andWhere('alert.userId = :userId', { userId });
    }
    
    if (status) {
      query.andWhere('alert.status = :status', { status });
    }
    
    return query.orderBy('alert.createdAt', 'DESC').getMany();
  }

  async handleAlert(alertId: number, handlerId: number, result: string) {
    return this.alertRepository.update(alertId, {
      status: 'resolved',
      handlerId,
      handleTime: new Date(),
      handleResult: result
    });
  }

  async getStats() {
    const total = await this.alertRepository.count();
    const pending = await this.alertRepository.count({ where: { status: 'pending' } });
    const red = await this.alertRepository.count({ where: { alertLevel: 'red' } });
    const orange = await this.alertRepository.count({ where: { alertLevel: 'orange' } });
    const yellow = await this.alertRepository.count({ where: { alertLevel: 'yellow' } });

    return { total, pending, red, orange, yellow };
  }
}
