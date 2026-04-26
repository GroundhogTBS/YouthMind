import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ContentService } from './content.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('content')
export class ContentController {
  constructor(private readonly contentService: ContentService) {}

  @Public()
  @Get('articles')
  async getArticles(
    @Query('category') category?: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number
  ) {
    return this.contentService.getArticles(category, page, limit);
  }

  @Public()
  @Get('article/:id')
  async getArticle(@Param('id') id: number) {
    return this.contentService.getArticle(id);
  }

  @Public()
  @Get('categories')
  async getCategories() {
    return this.contentService.getCategories();
  }

  @Post('article')
  async createArticle(@Body() body: any) {
    return this.contentService.createArticle(body);
  }
}
