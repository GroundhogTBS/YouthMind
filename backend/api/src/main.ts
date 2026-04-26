import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.enableCors({
    origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:5173', 'http://localhost:5174'],
    credentials: true
  });
  
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    transform: true
  }));
  
  app.setGlobalPrefix('api');
  
  const port = process.env.PORT || 8000;
  await app.listen(port);
  console.log('='.repeat(50));
  console.log(`YouthMind API running on: http://localhost:${port}/api`);
  console.log('='.repeat(50));
}

bootstrap();
