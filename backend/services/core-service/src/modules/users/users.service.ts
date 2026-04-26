import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}

  async findByPhone(phone: string): Promise<User | null> {
    return this.usersRepository.findOne({ 
      where: { phone },
      select: ['id', 'phone', 'password', 'nickname', 'avatar', 'role', 'isActive']
    });
  }

  async findById(id: number): Promise<User | null> {
    return this.usersRepository.findOne({ where: { id } });
  }

  async create(phone: string, hashedPassword: string): Promise<User> {
    const user = this.usersRepository.create({
      phone,
      password: hashedPassword,
      nickname: `用户${phone.slice(-4)}`,
    });
    return this.usersRepository.save(user);
  }

  async updateProfile(id: number, data: Partial<User>): Promise<User> {
    await this.usersRepository.update(id, data);
    return this.findById(id);
  }

  async updatePassword(id: number, hashedPassword: string): Promise<void> {
    await this.usersRepository.update(id, { password: hashedPassword });
  }
}
