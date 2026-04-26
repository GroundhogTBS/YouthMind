import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { User } from '../user/user.entity';

@Entity('sessions')
export class Session {
  @PrimaryGeneratedColumn('increment', { type: 'integer' })
  id: number;

  @Column({ type: 'integer' })
  userId: number;

  @ManyToOne(() => User)
  @JoinColumn({ name: 'userId' })
  user: User;

  @Column({ type: 'text', nullable: true })
  title: string;

  @Column({ type: 'integer', default: 0 })
  messageCount: number;

  @Column({ type: 'datetime', nullable: true })
  lastMessageAt: Date;

  @Column({ type: 'integer', default: 1 })
  status: number;

  @CreateDateColumn()
  createdAt: Date;
}
