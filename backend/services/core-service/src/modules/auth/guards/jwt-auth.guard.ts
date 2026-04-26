import { Injectable, ExecutionContext } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  canActivate(context: ExecutionContext) {
    const request = context.switchToHttp().getRequest();
    const isPublic = this.isPublicRoute(request.path);
    
    if (isPublic) {
      return true;
    }
    
    return super.canActivate(context);
  }

  private isPublicRoute(path: string): boolean {
    const publicRoutes = [
      '/api/auth/login',
      '/api/auth/register',
      '/api/auth/send-sms',
      '/api/health',
    ];
    return publicRoutes.some(route => path.startsWith(route));
  }
}
