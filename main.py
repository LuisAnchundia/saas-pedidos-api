from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Punto de entrada: Inversion de control estructural
app = FastAPI(
    title="SaaS Pedidos API",
    description="Prototipo Agil Multitenant para gestion de pedidos de clientes",
    version="1.0.0",
)


class PedidoEntrada(BaseModel):
    cliente_final: str
    producto: str
    cantidad: int = Field(gt=0)
    total: float = Field(gt=0)


class PedidoEstado(BaseModel):
    estado: str


# Simulacion en memoria particionada por tenant (Inquilino)
BD_MEMORIA_PEDIDOS = {
    "tienda_norte": [
        {"id": 1, "cliente_final": "Juan Perez", "producto": "Laptop", "cantidad": 1, "total": 1000.0, "estado": "pendiente"},
        {"id": 2, "cliente_final": "Ana Torres", "producto": "Mouse", "cantidad": 3, "total": 90.0, "estado": "pagado"},
        {"id": 3, "cliente_final": "Carlos Ruiz", "producto": "Teclado", "cantidad": 2, "total": 150.0, "estado": "enviado"},
    ],
    "tienda_sur": [
        {"id": 1, "cliente_final": "Maria Lopez", "producto": "Smartphone", "cantidad": 2, "total": 1200.0, "estado": "pagado"},
        {"id": 2, "cliente_final": "Pedro Gomez", "producto": "Tablet", "cantidad": 1, "total": 450.0, "estado": "pendiente"},
    ],
}


# ---------- Funciones auxiliares ----------
def obtener_tenant(tenant_id: str) -> list:
    """Devuelve los pedidos del tenant o lanza 404 si no existe."""
    if tenant_id not in BD_MEMORIA_PEDIDOS:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return BD_MEMORIA_PEDIDOS[tenant_id]


def buscar_pedido(pedidos: list, pedido_id: int) -> dict:
    """Busca un pedido por id dentro de la lista o lanza 404."""
    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            return pedido
    raise HTTPException(status_code=404, detail="Pedido no encontrado")



@app.get("/")
async def estado_servicio():
    return {
        "servicio": "SaaS Pedidos Activo",
        "arquitectura": "Multitenant API-first / JSON Puro",
        "version": "1.0.0",
    }


# Listar todos los pedidos de un tenant
@app.get("/api/{tenant_id}/pedidos")
async def listar_pedidos_por_tenant(tenant_id: str):
    pedidos = obtener_tenant(tenant_id)
    return {"tenant_id": tenant_id, "pedidos": pedidos}


@app.get("/api/{tenant_id}/pedidos/{pedido_id}")
async def obtener_pedido_por_id(tenant_id: str, pedido_id: int):
    if tenant_id not in BD_MEMORIA_PEDIDOS:
        raise HTTPException(status_code=404, detail="Empresa (Tenant) no registrada")

    # Buscar el pedido asegurando el aislamiento por tenant
    pedido = next((p for p in BD_MEMORIA_PEDIDOS[tenant_id] if p["id"] == pedido_id), None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado para este tenant")

    return {"tenant": tenant_id, "pedido": pedido}


# Actualizar el estado de un pedido
@app.put("/api/{tenant_id}/pedidos/{pedido_id}/estado")
async def actualizar_estado(tenant_id: str, pedido_id: int, datos: PedidoEstado):
    pedidos = obtener_tenant(tenant_id)
    pedido = buscar_pedido(pedidos, pedido_id)
    pedido["estado"] = datos.estado
    return pedido


# Eliminar un pedido
@app.delete("/api/{tenant_id}/pedidos/{pedido_id}")
async def eliminar_pedido(tenant_id: str, pedido_id: int):
    pedidos = obtener_tenant(tenant_id)
    pedido = buscar_pedido(pedidos, pedido_id)
    pedidos.remove(pedido)
    return {"mensaje": "Pedido eliminado", "pedido": pedido}
