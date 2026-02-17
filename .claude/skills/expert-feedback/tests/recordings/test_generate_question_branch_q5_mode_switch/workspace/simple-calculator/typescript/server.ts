// Express API Server - Intentionally flawed
// NO validation, NO error handling, NO documentation

import express from 'express';
import { add, subtract, multiply, divide, modulo } from './calculator';

const app = express();
app.use(express.json());

app.post('/add', (req, res) => {
  const result = add(req.body.a, req.body.b);
  res.json({ result });
});

app.post('/subtract', (req, res) => {
  const result = subtract(req.body.a, req.body.b);
  res.json({ result });
});

app.post('/multiply', (req, res) => {
  const result = multiply(req.body.a, req.body.b);
  res.json({ result });
});

app.post('/divide', (req, res) => {
  const result = divide(req.body.a, req.body.b);
  res.json({ result });
});

app.post('/modulo', (req, res) => {
  const result = modulo(req.body.a, req.body.b);
  res.json({ result });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Calculator API running on port ${PORT}`);
});
