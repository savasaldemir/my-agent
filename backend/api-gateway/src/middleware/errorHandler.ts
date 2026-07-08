import { Request, Response, NextFunction } from 'express';
import { getLogger } from './logger';

const logger = getLogger();

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  logger.error(error);

  if (error instanceof AppError) {
    return res.status(error.statusCode).json({
      error: error.message,
      statusCode: error.statusCode,
    });
  }

  res.status(500).json({
    error: 'Internal Server Error',
    statusCode: 500,
  });
};
