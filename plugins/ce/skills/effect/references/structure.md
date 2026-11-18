# Structuring Effect code

Read when an `Effect.gen` body keeps growing, when deciding where a branch or a helper goes, or when refactoring a module for readability. Effect makes it cheap to put everything in one generator, and the result is hard to read: dependency wiring, decisions and I/O interleaved in one long body.

## A generator body is a list of steps

An `Effect.gen` body should read as the operation's steps in order, each one a call. When a new case shows up, give it a named step (an `Effect.fn` or a plain function) and call it from the body, rather than adding another inline branch:

```ts
export const checkout = Effect.fn("orders.checkout")(function* (cartId: CartId) {
  const cart = yield* loadCart(cartId)
  const plan = planCheckout(cart, yield* Inventory.snapshot)
  if (plan._tag === "Rejected") return yield* new CheckoutRejected({ reason: plan.reason })
  const order = yield* placeOrder(plan)
  yield* notifyCustomer(order)
  return order
})
```

A reviewer reads the body to learn what happens and opens a step only to learn how. Name each step after what it achieves, and give `Effect.fn` a dotted name (`module.step`), since it becomes the span name in traces.

## Decide in a pure function, act in the Effect

When the code picks between outcomes (launch or print, retry or give up, approve or reject), compute the choice in a plain function over values and return a tagged result. The Effect around it gathers the inputs, calls the function, then acts on the tag. `planCheckout` above is that function: it takes data, never yields a service, and returns `{ _tag: "Ready", ... } | { _tag: "Rejected", reason }`.

The rules then sit in one place with a visible order (first matching rule wins), and the decision is tested with plain inputs and no layers, which leaves the Effect tests to cover the wiring. A safety rule such as "untrusted input never reaches the automatic path" belongs in this function, where one test pins it, rather than spread over the branches of a generator.

Pure helpers stay pure all the way down. Rendering, formatting and decisions take the values they need as arguments; they don't `yield*` a service to look something up, which would pull a requirement and a layer into every test of them.

## One owner per shared helper

When a second caller needs a helper that lives inside the first caller's module (one command importing from another command), move the helper into a module named for its concept and have both import it there. The modules then depend in one direction and nobody has to read one feature's module to find another's helper.

The same goes for types: when several modules in a directory share shapes, put them in that directory's own `types.ts` and have every module import from it. That keeps imports flowing one way and avoids type-only cycles.
