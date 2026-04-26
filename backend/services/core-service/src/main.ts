import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.enableCors({
    origin: ['http://localhost:3000', 'http://localhost:3001'],
    credentials: true,
  });
  
  app.setGlobalPrefix('api');
  
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    transform: true,
  }));
  
  const port = process.env.PORT || 8001;
  await app.listen(port);
  
  console.log('='.repeat(50));
  console.log(`YouthMind Core Service Running on port ${port}`);
  console.log(`API: http://localhost:${port}/api`);
  console.log('='.repeat(50));
}

bootstrap();
