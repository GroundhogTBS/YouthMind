import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { User } from '../user/user.entity';

@Entity('alert_events')
export class AlertEvent {
  @PrimaryGeneratedColumn('increment', { type: 'integer' })
  id: number;

  @Column({ type: 'integer' })
  userId: number;

  @ManyToOne(() => User)
  @JoinColumn({ name: 'userId' })
  user: User;

  @Column({ type: 'text' })
  alertLevel: string;

  @Column({ type: 'text' })
  alertType: string;

  @Column({ type: 'text' })
  triggerSource: string;

  @Column({ type: 'text', nullable: true })
  triggerContent: string;

  @Column({ type: 'text', nullable: true })
  triggerKeywords: string;

  @Column({ type: 'integer', default: 0 })
  riskScore: number;

  @Column({ type: 'text', default: 'pending' })
  status: string;

  @Column({ type: 'integer', nullable: true })
  handlerId: number;

  @Column({ type: 'datetime', nullable: true })
  handleTime: Date;

  @Column({ type: 'text', nullable: true })
  handleResult: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
