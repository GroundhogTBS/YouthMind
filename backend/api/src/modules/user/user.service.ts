import { Injectable, BadRequestException, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { User } from './user.entity';
import { TeenProfile } from './teen-profile.entity';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(TeenProfile)
    private profileRepository: Repository<TeenProfile>,
    private jwtService: JwtService
  ) {}

  async register(phone: string, password: string, nickname?: string) {
    const existingUser = await this.userRepository.findOne({ where: { phone } });
    if (existingUser) {
      throw new BadRequestException('该手机号已注册');
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = this.userRepository.create({
      phone,
      password: hashedPassword,
      nickname: nickname || `用户${phone.slice(-4)}`,
      userType: 'teen'
    });

    await this.userRepository.save(user);

    const profile = this.profileRepository.create({ userId: user.id });
    await this.profileRepository.save(profile);

    return this.generateToken(user);
  }

  async login(phone: string, password: string) {
    const user = await this.userRepository
      .createQueryBuilder('user')
      .where('user.phone = :phone', { phone })
      .addSelect('user.password')
      .getOne();

    if (!user) {
      throw new UnauthorizedException('用户不存在');
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('密码错误');
    }

    await this.userRepository.update(user.id, {
      lastLoginAt: new Date()
    });

    return this.generateToken(user);
  }

  async getProfile(userId: number) {
    const user = await this.userRepository.findOne({ where: { id: userId } });
    const profile = await this.profileRepository.findOne({ where: { userId } });
    return { user, profile };
  }

  async updateProfile(userId: number, data: Partial<TeenProfile>) {
    await this.profileRepository.update({ userId }, data);
    return this.getProfile(userId);
  }

  private generateToken(user: User) {
    const payload = { sub: user.id, phone: user.phone, userType: user.userType };
    return {
      accessToken: this.jwtService.sign(payload),
      user: {
        id: user.id,
        phone: user.phone,
        nickname: user.nickname,
        avatar: user.avatar,
        userType: user.userType
      }
    };
  }
}
