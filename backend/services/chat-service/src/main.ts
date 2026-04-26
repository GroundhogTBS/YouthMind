import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.enableCors({
    origin: ['http://localhost:3000', 'http://localhost:3001'],
    credentials: true,
  });
  
  app.setGlobalPrefix('api');
  
  const port = process.env.PORT || 8002;
  await app.listen(port);
  
  console.log('='.repeat(50));
  console.log(`YouthMind Chat Service Running on port ${port}`);
  console.log(`API: http://localhost:${port}/api`);
  console.log('='.repeat(50));
}

bootstrap();
