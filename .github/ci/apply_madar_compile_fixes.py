from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def read(rel):
    return (root / rel).read_text()

def write(rel, text):
    (root / rel).write_text(text)

def replace(rel, old, new):
    text = read(rel)
    if old not in text:
        raise RuntimeError(f"Expected source pattern missing: {rel}: {old[:80]!r}")
    write(rel, text.replace(old, new))

def add_imports(rel, imports):
    text = read(rel)
    lines = text.splitlines()
    existing = {line.strip() for line in lines if line.startswith("import ")}
    additions = [f"import {item}" for item in imports if f"import {item}" not in existing]
    if additions:
        package_index = next(i for i, line in enumerate(lines) if line.startswith("package "))
        lines[package_index + 1:package_index + 1] = [""] + additions
        write(rel, "\n".join(lines) + "\n")

remote_files = [
    "app/src/main/java/com/shift/app/data/remote/AssetRemoteSyncDataSource.kt",
    "app/src/main/java/com/shift/app/data/remote/DebtRemoteSyncDataSource.kt",
    "app/src/main/java/com/shift/app/data/remote/GoalRemoteSyncDataSource.kt",
    "app/src/main/java/com/shift/app/data/remote/LedgerRemoteSyncDataSource.kt",
    "app/src/main/java/com/shift/app/data/remote/ReferenceDataRemoteSyncDataSource.kt",
    "app/src/main/java/com/shift/app/data/remote/SettingsRemoteSyncDataSource.kt",
]
for rel in remote_files:
    add_imports(rel, ["javax.inject.Inject", "javax.inject.Singleton"])
add_imports(
    "app/src/main/java/com/shift/app/data/remote/GoalRemoteSyncDataSource.kt",
    ["java.time.Instant", "java.time.ZoneOffset"],
)

unit_signatures = {
    "app/src/main/java/com/shift/app/data/remote/AssetRemoteSyncDataSource.kt": [
        "override suspend fun pullAssets(forceFull: Boolean) = withContext(Dispatchers.IO) {",
        "override suspend fun pullAssetTransactions(forceFull: Boolean) = withContext(Dispatchers.IO) {",
        "override suspend fun pullAssetValuations() = withContext(Dispatchers.IO) {",
        "override suspend fun pullCurrencyAssetLots(forceFull: Boolean) = withContext(Dispatchers.IO) {",
        "override suspend fun pullCurrencyAssetSaleAllocations(forceFull: Boolean) = withContext(Dispatchers.IO) {",
    ],
    "app/src/main/java/com/shift/app/data/remote/DebtRemoteSyncDataSource.kt": [
        "override suspend fun pullDebts() = withContext(Dispatchers.IO) {",
        "override suspend fun pullDebtLedger() = withContext(Dispatchers.IO) {",
    ],
    "app/src/main/java/com/shift/app/data/remote/GoalRemoteSyncDataSource.kt": [
        "override suspend fun pullFinancialGoals() = withContext(Dispatchers.IO) {",
    ],
    "app/src/main/java/com/shift/app/data/remote/LedgerRemoteSyncDataSource.kt": [
        "override suspend fun pullTransactions() = withContext(Dispatchers.IO) {",
        "override suspend fun pullBalanceTransactions(forceFull: Boolean) = withContext(Dispatchers.IO) {",
        "override suspend fun pullLedgerHistoryMigrations(forceFull: Boolean) = withContext(Dispatchers.IO) {",
    ],
    "app/src/main/java/com/shift/app/data/remote/ReferenceDataRemoteSyncDataSource.kt": [
        "override suspend fun pullIncomeSources() = withContext(Dispatchers.IO) {",
        "override suspend fun pullExpenseBeneficiaries() = withContext(Dispatchers.IO) {",
    ],
    "app/src/main/java/com/shift/app/data/remote/SettingsRemoteSyncDataSource.kt": [
        "override suspend fun pullSettings() = withContext(Dispatchers.IO) {",
    ],
}
for rel, signatures in unit_signatures.items():
    text = read(rel)
    for signature in signatures:
        if signature in text:
            text = text.replace(signature, signature.replace(" = withContext", ": Unit = withContext"))
    write(rel, text)

replace(
    "app/src/main/java/com/shift/app/data/remote/LedgerRemoteSyncDataSource.kt",
    """    override suspend fun pullPayments(\n        forceFull: Boolean,\n        repairAfterPull: Boolean\n    ) = withContext(Dispatchers.IO) {""",
    """    override suspend fun pullPayments(\n        forceFull: Boolean,\n        repairAfterPull: Boolean\n    ): Unit = withContext(Dispatchers.IO) {""",
)

replace(
    "app/src/main/java/com/shift/app/feature/goals/data/GoalCompletionAdapter.kt",
    "class GoalCompletionAdapter @Inject constructor(",
    "internal class GoalCompletionAdapter @Inject constructor(",
)
replace(
    "app/src/main/java/com/shift/app/feature/goals/data/GoalCompletionAdapter.kt",
    "private val costCompletion: RoomCostGoalCompletion,",
    "private val costCompletion: CompleteCostGoal,",
)
replace(
    "app/src/main/java/com/shift/app/feature/goals/data/GoalCompletionAdapter.kt",
    """    override suspend fun completeAssetPurchase(request: AssetGoalCompletionRequest) = assetCompletion.complete(request)\n    override suspend fun completeCostGoal(request: CompleteCostGoalRequest) = costCompletion.complete(request)\n    override suspend fun recordDebtPayment(request: GoalDebtPaymentRequest) = debtPayment.record(request)""",
    """    override suspend fun completeAssetPurchase(request: AssetGoalCompletionRequest) {\n        assetCompletion.complete(request)\n    }\n\n    override suspend fun completeCostGoal(request: CompleteCostGoalRequest) {\n        costCompletion.complete(request)\n    }\n\n    override suspend fun recordDebtPayment(request: GoalDebtPaymentRequest) {\n        debtPayment.record(request)\n    }""",
)

replace(
    "app/src/main/java/com/shift/app/feature/auth/data/WorkManagerSessionWorkController.kt",
    "override suspend fun cancelAndAwaitSessionWork() = withContext(Dispatchers.IO) {",
    "override suspend fun cancelAndAwaitSessionWork(): Unit = withContext(Dispatchers.IO) {",
)
replace(
    "app/src/main/java/com/shift/app/sync/PreferencesSyncCheckpointStore.kt",
    "override suspend fun setLastSuccessfulSync(value: Long) = preferences.setLastSync(value)",
    """override suspend fun setLastSuccessfulSync(value: Long) {\n        preferences.setLastSync(value)\n    }""",
)
replace(
    "app/src/main/java/com/shift/app/sync/PreferencesSyncCheckpointStore.kt",
    """override suspend fun setParticipantCheckpoint(key: String, value: Long) =\n        preferences.setSyncCheckpoint(key, value)""",
    """override suspend fun setParticipantCheckpoint(key: String, value: Long) {\n        preferences.setSyncCheckpoint(key, value)\n    }""",
)

replace(
    "app/src/main/java/com/shift/app/viewmodel/TransactionsViewModel.kt",
    "import com.shift.app.domain.goals.funding.ActiveGoalAllocation",
    "import com.shift.app.data.repository.ActiveGoalAllocation",
)
replace(
    "app/src/main/java/com/shift/app/feature/goals/presentation/GoalEditorScreen.kt",
    "options: List<com.shift.app.viewmodel.DebtAccountOption>,",
    "options: List<DebtAccountOption>,",
)
add_imports(
    "app/src/main/java/com/shift/app/ui/screens/PaymentsScreen.kt",
    ["com.shift.app.feature.assets.presentation.assetTypeLabel"],
)
replace(
    "app/src/main/java/com/shift/app/feature/debts/presentation/DebtActionSheets.kt",
    "@Composable\ninternal fun CreateDebtAccountSheet(",
    "@OptIn(ExperimentalMaterial3Api::class)\n@Composable\ninternal fun CreateDebtAccountSheet(",
)

# Asset atomic RPC needs the same legacy ledger serialization as LedgerRemoteSyncDataSource.
ledger_rel = "app/src/main/java/com/shift/app/data/remote/LedgerRemoteSyncDataSource.kt"
asset_rel = "app/src/main/java/com/shift/app/data/remote/AssetRemoteSyncDataSource.kt"
ledger = read(ledger_rel)
asset = read(asset_rel)
if "private fun BalanceTransaction.toRemote(uid: String): RemoteBalanceTransaction" not in asset:
    start = ledger.index("    private fun Transaction.toRemote(uid: String): RemoteTransaction {")
    end = ledger.index("\n\n\n    override suspend fun repairIncompletePaymentOperationsForSync()", start)
    mappings = ledger[start:end]
    insert_at = asset.rfind("\n}")
    if insert_at < 0:
        raise RuntimeError("AssetRemoteSyncDataSource closing brace not found")
    asset = asset[:insert_at] + "\n\n" + mappings + "\n" + asset[insert_at:]
    write(asset_rel, asset)

print("Madar compile repairs applied")
