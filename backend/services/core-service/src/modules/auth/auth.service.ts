import { Injectable, UnauthorizedException, BadRequestException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UsersService } from '../users/users.service';
import { RegisterDto, LoginDto } from './dto/auth.dto';

@Injectable()
export class AuthService {
  private smsCodes = new Map<string, { code: string; expiresAt: number }>();

  constructor(
    private usersService: UsersService,
    private jwtService: JwtService,
  ) {}

  async register(dto: RegisterDto) {
    const existingUser = await this.usersService.findByPhone(dto.phone);
    if (existingUser) {
      throw new BadRequestException('该手机号已注册');
    }

    const hashedPassword = await bcrypt.hash(dto.password, 10);
    const user = await this.usersService.create(dto.phone, hashedPassword);

    const tokens = await this.generateTokens(user.id, user.phone);
    return {
      user: { ...user, password: undefined },
      ...tokens,
    };
  }

  async login(dto: LoginDto) {
    const user = await this.usersService.findByPhone(dto.phone);
    if (!user) {
      throw new UnauthorizedException('手机号或密码错误');
    }

    const isPasswordValid = await bcrypt.compare(dto.password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('手机号或密码错误');
    }

    if (!user.isActive) {
      throw new UnauthorizedException('账号已被禁用');
    }

    const tokens = await this.generateTokens(user.id, user.phone);
    return {
      user: { ...user, password: undefined },
      ...tokens,
    };
  }

  async sendSms(phone: string) {
    const code = Math.random().toString().slice(-6);
    const expiresAt = Date.now() + 5 * 60 * 1000;
    
    this.smsCodes.set(phone, { code, expiresAt });
    
    console.log(`[SMS] 发送验证码到 ${phone}: ${code}`);
    
    return { message: '验证码已发送' };
  }

  async verifySms(phone: string, code: string): Promise<boolean> {
    const stored = this.smsCodes.get(phone);
    if (!stored) {
      return false;
    }
    
    if (Date.now() > stored.expiresAt) {
      this.smsCodes.delete(phone);
      return false;
    }
    
    const isValid = stored.code === code;
    if (isValid) {
      this.smsCodes.delete(phone);
    }
    
    return isValid;
  }

  private async generateTokens(userId: number, phone: string) {
    const payload = { userId, phone };
    
    const accessToken = this.jwtService.sign(payload, {
      expiresIn: '2h',
    });
    
    const refreshToken = this.jwtService.sign(payload, {
      expiresIn: '7d',
    });

    return { accessToken, refreshToken };
  }

  async refreshTokens(refreshToken: string) {
    try {
      const payload = this.jwtService.verify(refreshToken);
      const user = await this.usersService.findById(payload.userId);
      
      if (!user || !user.isActive) {
        throw new UnauthorizedException('用户不存在或已被禁用');
      }

      return this.generateTokens(user.id, user.phone);
    } catch {
      throw new UnauthorizedException('无效的刷新令牌');
    }
  }
}
