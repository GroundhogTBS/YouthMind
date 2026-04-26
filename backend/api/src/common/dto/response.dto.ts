export class ResponseDto<T> {
  code: number;
  message: string;
  data: T;

  static success<T>(data: T, message = 'success'): ResponseDto<T> {
    const dto = new ResponseDto<T>();
    dto.code = 0;
    dto.message = message;
    dto.data = data;
    return dto;
  }

  static error<T>(message: string, code = -1): ResponseDto<T> {
    const dto = new ResponseDto<T>();
    dto.code = code;
    dto.message = message;
    dto.data = null as T;
    return dto;
  }
}
