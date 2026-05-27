class Lectura {
  final int id;
  final double valor;
  final int estacionId;

  Lectura({
    required this.id,
    required this.valor,
    required this.estacionId,
  });

  factory Lectura.fromJson(Map<String, dynamic> json) {
    return Lectura(
      id: json['id'],
      valor: (json['valor'] as num).toDouble(),
      estacionId: json['estacion_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'valor': valor,
      'estacion_id': estacionId,
    };
  }
}