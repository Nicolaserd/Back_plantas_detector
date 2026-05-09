---
trigger: always_on
---

Diseña el backend de forma genérica, modular y escalable. Antes de crear cualquier función, clase, archivo, endpoint o módulo nuevo, revisa todo el código existente para identificar si ya existe una pieza reutilizable. Si existe, reutilízala o extiéndela sin romper la arquitectura. No dupliques validaciones, configuración, respuestas, errores, transformaciones, reglas de negocio, acceso a datos ni lógica de proveedores.

Mantén rutas delgadas, servicios con responsabilidad clara, contratos estables, configuración centralizada y módulos independientes. No acoples el núcleo del sistema a un único caso de uso, proveedor, modelo, base de datos, formato o protocolo. Si algo puede cambiar en el futuro, aíslalo detrás de una interfaz, servicio, provider, adapter o clase base.

DRY es obligatorio en cada peticion revisar todo el codigo para ver si se puede reutilizar, pero nunca debe justificar mezclar responsabilidades, crear dependencias circulares o romper la separación por capas. La prioridad es: arquitectura limpia, escalabilidad, claridad, reutilización y simplicidad.