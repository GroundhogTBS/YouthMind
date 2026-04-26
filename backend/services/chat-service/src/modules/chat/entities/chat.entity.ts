import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn, ManyToOne, OneToMany, JoinColumn } from 'typeorm';

@Entity('chat_sessions')
export class ChatSession {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  userId: number;

  @Column({ length: 100, default: '新对话' })
  title: string;

  @Column({ default: true })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @OneToMany(() => ChatMessage, message => message.session)
  messages: ChatMessage[];
}

@Entity('chat_messages')
export class ChatMessage {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  sessionId: number;

  @Column({ length: 20 })
  role: string;

  @Column({ type: 'text' })
  content: string;

  @Column({ length: 50, nullable: true })
  emotion: string;

  @Column({ type: 'float', nullable: true })
  emotionScore: number;

  @Column({ length: 20, nullable: true })
  riskLevel: string;

  @CreateDateColumn()
  createdAt: Date;

  @ManyToOne(() => ChatSession, session => session.messages)
  @JoinColumn({ name: 'sessionId' })
  session: ChatSession;
}
