"""
Comando de gestión: train_ai
=============================
Entrena los tres módulos de IA de CrowdMentor.

Uso
---
    python manage.py train_ai                        # Entrena todos los módulos
    python manage.py train_ai --module predictor     # Solo predictor de éxito
    python manage.py train_ai --module mentors       # Solo recomendador de mentores
    python manage.py train_ai --module advisor       # Solo asesor de mejoras
    python manage.py train_ai --kaggle ruta/archivo.csv  # Entrenar con CSV de Kaggle
    python manage.py train_ai --status               # Ver estado de los modelos

Descripción de cada módulo
---------------------------
  predictor : Regresión Logística + TF-IDF para predecir éxito de proyectos.
              Requiere CSV de Kaggle (Kickstarter) o datos de la BD.
  mentors   : Indexación TF-IDF de perfiles de mentores para recomendación.
              Lee directamente de la BD de CrowdMentor.
  advisor   : Corpus TF-IDF de proyectos exitosos para generar sugerencias.
              Lee proyectos financiados ≥ 80% de la BD.
"""
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Entrena los módulos de IA de CrowdMentor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            choices=['predictor', 'mentors', 'advisor', 'all'],
            default='all',
            help='Módulo a entrenar (por defecto: all)',
        )
        parser.add_argument(
            '--kaggle',
            type=str,
            default=None,
            metavar='CSV_PATH',
            help='Ruta al CSV de Kaggle Kickstarter para entrenar el predictor',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Muestra el estado de los modelos entrenados y sale',
        )
        parser.add_argument(
            '--eval-split',
            type=float,
            default=0.20,
            metavar='FRAC',
            help='Fracción de datos para evaluación (default: 0.20)',
        )

    def handle(self, *args, **options):
        if options['status']:
            self._print_status()
            return

        module = options['module']
        kaggle_csv = options['kaggle']
        eval_split = options['eval_split']

        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(self.style.SUCCESS('   CrowdMentor - Sistema de IA: Entrenamiento'))
        self.stdout.write(self.style.SUCCESS('=' * 55))

        if module in ('predictor', 'all'):
            self._train_predictor(kaggle_csv, eval_split)

        if module in ('mentors', 'all'):
            self._train_mentors()

        if module in ('advisor', 'all'):
            self._train_advisor()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('[OK] Entrenamiento completado.'))
        self.stdout.write('  Los modelos se guardaron en saved_models/')

    # ── Predictor de éxito ────────────────────────────

    def _train_predictor(self, kaggle_csv: str | None, eval_split: float):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('[ Módulo 1 ] Predictor de Éxito de Proyectos'))

        try:
            from ml_models.success_predictor import get_predictor
        except ImportError as e:
            self.stderr.write(f'  Error importando módulo: {e}')
            return

        predictor = get_predictor()

        # Intentar cargar datos: Kaggle tiene prioridad, luego BD, luego auto-detect
        if kaggle_csv:
            texts, labels = self._load_kaggle_data(kaggle_csv)
            source = f'Kaggle CSV especificado ({len(texts)} proyectos)'
        else:
            # Intentar auto-detectar CSVs en datasets/
            try:
                texts, labels = self._load_kaggle_data(None)
                source = f'Kaggle CSVs auto-detectados ({len(texts)} proyectos)'
            except Exception:
                texts, labels = self._load_crowdmentor_projects()
                source = f'BD CrowdMentor ({len(texts)} proyectos)'

        if len(texts) < 10:
            self.stdout.write(
                self.style.WARNING(
                    f'  [WARN] Datos insuficientes ({len(texts)} proyectos). '
                    'Usa --kaggle para un CSV de Kickstarter.'
                )
            )
            self.stdout.write(
                '  Descarga el dataset en: '
                'https://www.kaggle.com/datasets/kemical/kickstarter-projects'
            )
            return

        self.stdout.write(f'  Fuente: {source}')
        self.stdout.write(f'  Distribución: {sum(labels)} exitosos / {len(labels)-sum(labels)} fallidos')
        self.stdout.write('  Entrenando Regresión Logística con TF-IDF...')

        try:
            metrics = predictor.train(texts, labels, eval_split=eval_split)
            self.stdout.write(self.style.SUCCESS(f'  [OK] Accuracy : {metrics["accuracy"]:.4f}'))
            self.stdout.write(self.style.SUCCESS(f'  [OK] Precision: {metrics["precision"]:.4f}'))
            self.stdout.write(self.style.SUCCESS(f'  [OK] Recall   : {metrics["recall"]:.4f}'))
            self.stdout.write(self.style.SUCCESS(f'  [OK] F1-Score : {metrics["f1"]:.4f}'))
            self.stdout.write(self.style.SUCCESS(f'  [OK] ROC-AUC  : {metrics["roc_auc"]:.4f}'))
            self.stdout.write(f'  Reporte completo:\n{metrics["report"]}')
            self._save_training_plots(metrics)
        except Exception as exc:
            self.stderr.write(f'  Error durante entrenamiento: {exc}')

    def _save_training_plots(self, metrics: dict) -> None:
        """Guarda gráficas de evaluación del predictor en la carpeta graficas/."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except Exception:
            self.stdout.write(
                self.style.WARNING(
                    '  [WARN] No se pudo importar matplotlib. Instálalo para generar gráficas: pip install matplotlib'
                )
            )
            return

        try:
            import numpy as np
            from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(f'  [WARN] No se pudieron preparar métricas para gráficas: {exc}')
            )
            return

        y_test = np.array(metrics.get('y_test', []))
        y_pred = np.array(metrics.get('y_pred', []))
        y_proba = np.array(metrics.get('y_proba', []))
        if len(y_test) == 0 or len(y_pred) == 0 or len(y_proba) == 0:
            self.stdout.write(self.style.WARNING('  [WARN] No hay datos suficientes para generar gráficas.'))
            return

        root_dir = Path(__file__).resolve().parents[3]
        charts_dir = root_dir / 'graficas'
        charts_dir.mkdir(parents=True, exist_ok=True)

        # 1) Barras de métricas principales
        metric_names = ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC']
        metric_values = [
            float(metrics['accuracy']),
            float(metrics['precision']),
            float(metrics['recall']),
            float(metrics['f1']),
            float(metrics['roc_auc']),
        ]
        plt.figure(figsize=(8, 5))
        bars = plt.bar(metric_names, metric_values)
        plt.ylim(0.0, 1.0)
        plt.title('Resumen de metricas del modelo')
        plt.ylabel('Puntaje')
        for bar, value in zip(bars, metric_values):
            plt.text(bar.get_x() + bar.get_width() / 2, value + 0.01, f'{value:.3f}', ha='center')
        plt.tight_layout()
        plt.savefig(charts_dir / 'metricas_resumen.png', dpi=150)
        plt.close()

        # 2) Matriz de confusión
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
        plt.figure(figsize=(6, 5))
        plt.imshow(cm, interpolation='nearest')
        plt.title('Matriz de confusion')
        plt.colorbar()
        tick_marks = np.arange(2)
        plt.xticks(tick_marks, ['Fallido', 'Exitoso'])
        plt.yticks(tick_marks, ['Fallido', 'Exitoso'])
        plt.xlabel('Prediccion')
        plt.ylabel('Valor real')
        thresh = cm.max() / 2 if cm.size > 0 else 0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, str(cm[i, j]), ha='center', va='center',
                         color='white' if cm[i, j] > thresh else 'black')
        plt.tight_layout()
        plt.savefig(charts_dir / 'matriz_confusion.png', dpi=150)
        plt.close()

        # 3) Curva ROC
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        plt.figure(figsize=(7, 5))
        plt.plot(fpr, tpr, label=f"AUC = {float(metrics['roc_auc']):.3f}")
        plt.plot([0, 1], [0, 1], linestyle='--')
        plt.title('Curva ROC')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc='lower right')
        plt.tight_layout()
        plt.savefig(charts_dir / 'curva_roc.png', dpi=150)
        plt.close()

        # 4) Curva Precision-Recall
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_proba)
        plt.figure(figsize=(7, 5))
        plt.plot(recall_curve, precision_curve)
        plt.title('Curva Precision-Recall')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.tight_layout()
        plt.savefig(charts_dir / 'curva_precision_recall.png', dpi=150)
        plt.close()

        # 5) Distribución de clases del dataset
        class_counts = metrics.get('class_counts', {})
        class_labels = ['Fallido', 'Exitoso']
        class_values = [
            int(class_counts.get('fallido', 0)),
            int(class_counts.get('exitoso', 0)),
        ]
        plt.figure(figsize=(6, 5))
        bars = plt.bar(class_labels, class_values)
        plt.title('Distribucion de clases en entrenamiento')
        plt.ylabel('Cantidad de proyectos')
        for bar, value in zip(bars, class_values):
            plt.text(bar.get_x() + bar.get_width() / 2, value + 0.5, str(value), ha='center')
        plt.tight_layout()
        plt.savefig(charts_dir / 'distribucion_clases.png', dpi=150)
        plt.close()

        # 6) Distribución de probabilidades predichas
        plt.figure(figsize=(7, 5))
        plt.hist(y_proba, bins=20)
        plt.title('Distribucion de probabilidades predichas')
        plt.xlabel('Probabilidad de exito')
        plt.ylabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(charts_dir / 'distribucion_probabilidades.png', dpi=150)
        plt.close()

        # 7) Accuracy por epocas (train vs validacion)
        epochs = metrics.get('epochs', [])
        train_acc = metrics.get('train_accuracy_by_epoch', [])
        val_acc = metrics.get('val_accuracy_by_epoch', [])
        if epochs and train_acc and val_acc:
            plt.figure(figsize=(8, 5))
            plt.plot(epochs, train_acc, marker='o', label='Train Accuracy')
            plt.plot(epochs, val_acc, marker='o', label='Validation Accuracy')
            plt.ylim(0.0, 1.0)
            plt.title('Accuracy por epocas')
            plt.xlabel('Epoca')
            plt.ylabel('Accuracy')
            plt.legend()
            plt.grid(alpha=0.2)
            plt.tight_layout()
            plt.savefig(charts_dir / 'accuracy_epocas.png', dpi=150)
            plt.close()

        self.stdout.write(self.style.SUCCESS(f'  [OK] Graficas guardadas en: {charts_dir}'))

    def _load_kaggle_data(self, csv_path: str | None) -> tuple[list[str], list[int]]:
        """
        Carga el dataset Kickstarter de Kaggle.
        Si csv_path es None, busca automáticamente en datasets/ los CSVs de Kickstarter.
        Si hay dos archivos, los fusiona para maximizar los datos de entrenamiento.
        """
        from ml_models.kaggle_trainer import load_kickstarter_data
        from pathlib import Path

        try:
            import pandas as pd  # noqa: F401
        except ImportError:
            raise CommandError('Instala pandas: pip install pandas')

        # ── Auto-detección de datasets si no se especificó ruta ──────────────
        if not csv_path:
            datasets_dir = Path(__file__).resolve().parents[3] / 'datasets'
            found = sorted(datasets_dir.glob('ks-projects-*.csv'))
            if not found:
                raise CommandError(
                    'No se encontró ningún CSV de Kickstarter en datasets/.\n'
                    'Descarga el dataset en:\n'
                    '  https://www.kaggle.com/datasets/kemical/kickstarter-projects\n'
                    'y coloca los archivos en la carpeta datasets/'
                )
            paths = [str(p) for p in found]
            self.stdout.write(
                f'  Auto-detectados {len(paths)} dataset(s): '
                + ', '.join(p.name for p in found)
            )
        else:
            paths = [p.strip() for p in csv_path.split(',') if p.strip()]

        self.stdout.write(f'  Cargando y fusionando {len(paths)} CSV(s)...')
        return load_kickstarter_data(paths)

    def _load_crowdmentor_projects(self) -> tuple[list[str], list[int]]:
        """Carga proyectos de la BD de CrowdMentor como datos de entrenamiento."""
        from core.models import Project

        projects = Project.objects.filter(is_active=True).select_related('category')
        texts  = []
        labels = []

        for p in projects:
            try:
                pct = float(p.amount_raised) / float(p.funding_goal)
            except Exception:
                pct = 0

            label = 1 if (pct >= 0.8 or p.status in ('funded', 'completed')) else 0
            texts.append(f"{p.title} {p.description}")
            labels.append(label)

        return texts, labels

    # ── Recomendador de mentores ──────────────────────

    def _train_mentors(self):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('[ Módulo 2 ] Recomendador de Mentores'))

        try:
            from ml_models.mentor_recommender import rebuild_mentor_index
        except ImportError as e:
            self.stderr.write(f'  Error importando módulo: {e}')
            return

        self.stdout.write('  Indexando perfiles de mentores con TF-IDF...')
        try:
            count = rebuild_mentor_index()
            if count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        '  [WARN] No se encontraron mentores aprobados en la BD. '
                        'Aprueba mentores desde el panel de administracion.'
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS(f'  [OK] {count} mentores indexados'))
        except Exception as exc:
            self.stderr.write(f'  Error: {exc}')

    # ── Asesor de mejoras ─────────────────────────────

    def _train_advisor(self):
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('[ Módulo 3 ] Asesor de Mejoras de Proyectos'))

        try:
            from ml_models.advisor import rebuild_advisor_corpus
        except ImportError as e:
            self.stderr.write(f'  Error importando módulo: {e}')
            return

        self.stdout.write('  Construyendo corpus de proyectos exitosos...')
        try:
            count = rebuild_advisor_corpus()
            if count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        '  [WARN] No hay proyectos con financiamiento suficiente '
                        'para construir el corpus. El asesor usara sugerencias basadas en reglas.'
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS(f'  [OK] {count} proyectos exitosos indexados'))
        except Exception as exc:
            self.stderr.write(f'  Error: {exc}')

    # ── Estado ────────────────────────────────────────

    def _print_status(self):
        from ml_models.config import (
            SUCCESS_PREDICTOR_PATH, MENTOR_MATRIX_PATH, ADVISOR_CORPUS_PATH
        )

        self.stdout.write(self.style.SUCCESS('=' * 45))
        self.stdout.write('   Estado de Modelos - CrowdMentor IA')
        self.stdout.write(self.style.SUCCESS('=' * 45))

        models = [
            ('Predictor de Éxito',     SUCCESS_PREDICTOR_PATH),
            ('Recomendador de Mentores', MENTOR_MATRIX_PATH),
            ('Asesor de Mejoras',       ADVISOR_CORPUS_PATH),
        ]

        for name, path in models:
            if path.exists():
                import os
                size_kb = os.path.getsize(path) / 1024
                self.stdout.write(
                    self.style.SUCCESS(f'  [OK] {name:<30} [{size_kb:.0f} KB]')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  [X] {name:<30} [no entrenado]')
                )

        self.stdout.write('')
        self.stdout.write('Para entrenar: python manage.py train_ai')
        self.stdout.write('Con Kaggle:    python manage.py train_ai --kaggle ruta/ks-projects.csv')
