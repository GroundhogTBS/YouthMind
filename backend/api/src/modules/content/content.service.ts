import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Article } from './article.entity';

@Injectable()
export class ContentService {
  constructor(
    @InjectRepository(Article)
    private articleRepository: Repository<Article>
  ) {}

  async getArticles(category?: string, page = 1, limit = 10) {
    const query = this.articleRepository.createQueryBuilder('article')
      .where('article.isPublished = 1');

    if (category) {
      query.andWhere('article.category = :category', { category });
    }

    const [items, total] = await query
      .orderBy('article.publishedAt', 'DESC')
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount();

    return { items, total, page, limit };
  }

  async getArticle(id: number) {
    const article = await this.articleRepository.findOne({ where: { id } });
    if (article) {
      await this.articleRepository.increment({ id }, 'viewCount', 1);
    }
    return article;
  }

  async createArticle(data: Partial<Article>) {
    const article = this.articleRepository.create({
      ...data,
      isPublished: 1,
      publishedAt: new Date()
    });
    return this.articleRepository.save(article);
  }

  async getCategories() {
    const result = await this.articleRepository
      .createQueryBuilder('article')
      .select('article.category', 'category')
      .addSelect('COUNT(*)', 'count')
      .where('article.isPublished = 1')
      .groupBy('article.category')
      .getRawMany();
    
    return result;
  }
}
