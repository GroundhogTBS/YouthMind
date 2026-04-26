import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Session } from './session.entity';
import { User } from '../user/user.entity';

@Entity('messages')
export class Message {
  @PrimaryGeneratedColumn('increment', { type: 'integer' })
  id: number;

  @Column({ type: 'integer' })
  sessionId: number;

  @ManyToOne(() => Session)
  @JoinColumn({ name: 'sessionId' })
  session: Session;

  @Column({ type: 'integer' })
  userId: number;

  @ManyToOne(() => User)
  @JoinColumn({ name: 'userId' })
  user: User;

  @Column({ type: 'text' })
  content: string;

  @Column({ type: 'text', default: 'user' })
  sender: string;

  @Column({ type: 'text', nullable: true })
  emotion: string;

  @Column({ type: 'real', nullable: true })
  emotionScore: number;

  @Column({ type: 'text', nullable: true })
  voiceUrl: string;

  @CreateDateColumn()
  createdAt: Date;
}
