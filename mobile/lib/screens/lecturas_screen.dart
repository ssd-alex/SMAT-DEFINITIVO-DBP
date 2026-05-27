import 'package:flutter/material.dart';
import '../models/lectura.dart';
import '../services/api_service.dart';

class LecturasScreen extends StatefulWidget {
  const LecturasScreen({super.key});

  @override
  State<LecturasScreen> createState() => _LecturasScreenState();
}

class _LecturasScreenState extends State<LecturasScreen> {
  late Future<List<Lectura>> futureLecturas;
  final ApiService apiService = ApiService();

  @override
  void initState() {
    super.initState();
    futureLecturas = apiService.fetchLecturas();
  }

  void _refrescar() {
    setState(() {
      futureLecturas = apiService.fetchLecturas();
    });
  }

  Color _colorPorValor(double valor) {
    if (valor > 70) return Colors.red.shade200;
    if (valor > 20) return Colors.amber.shade200;
    return Colors.green.shade200;
  }

  String _estadoPorValor(double valor) {
    if (valor > 70) return 'ALERTA';
    if (valor > 20) return 'PRECAUCIÓN';
    return 'NORMAL';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lecturas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refrescar,
          ),
        ],
      ),
      body: FutureBuilder<List<Lectura>>(
        future: futureLecturas,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('❌ ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No hay lecturas'));
          }

          final lecturas = snapshot.data!;
          return RefreshIndicator(
            onRefresh: () async => _refrescar(),
            child: ListView.builder(
              itemCount: lecturas.length,
              itemBuilder: (context, index) {
                final lectura = lecturas[index];
                final color = _colorPorValor(lectura.valor);
                final estado = _estadoPorValor(lectura.valor);

                return Card(
                  color: color,
                  margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  child: ListTile(
                    leading: Icon(
                      Icons.water_drop,
                      color: lectura.valor > 70 ? Colors.red : Colors.black87,
                    ),
                    title: Text(
                      'Valor: ${lectura.valor}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text('Estación ID: ${lectura.estacionId} • Estado: $estado'),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}